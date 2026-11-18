import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import UTC, datetime
from http.client import HTTPException, HTTPResponse
from pathlib import Path
from urllib.request import Request, urlopen
from zlib import error as ZlibError

TOP_N = 100
USER_AGENT = "Yuki Okamoto <cord@x56.cx>"
HTTP_TIMEOUT_SECONDS = 60
TMP_ROOT = Path("/tmp")
RESULTS_DIR = Path("results")
CHECK_COMMAND = ["cargo", "gevatter", "check", "--", "--workspace"]

CRATES_API = "https://crates.io/api/v1/crates"
CRATES_DOWNLOADS = "https://static.crates.io/crates"

class Crate:
    name: str
    version: str
    downloads: int
    def __init__(self, name, version, downloads):
        self.name = name
        self.version = version
        self.downloads = downloads

def http_get(url: str) -> HTTPResponse:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    return urlopen(request, timeout=HTTP_TIMEOUT_SECONDS)


def top_crates() -> list[Crate]:
    crates: list[Crate] = []
    query = f"?sort=downloads&per_page={min(TOP_N, 100)}"
    while query:
        with http_get(CRATES_API + query) as response:
            page = json.load(response)
        for item in page["crates"][:TOP_N - len(crates)]:
            name = item["name"]
            version = item["default_version"] or item["newest_version"]
            crate = Crate(name, version, item["downloads"])
            crates.append(crate)
        query = page["meta"]["next_page"]
        if len(crates) == TOP_N or not query:
            break
        time.sleep(1)
    return crates


def check_crate(rank: int, name: str, version: str, downloads: int):
    package = f"{name}-{version}"
    download_url = f"{CRATES_DOWNLOADS}/{name}/{package}.crate"
    report_path = RESULTS_DIR / f"{package}.log"
    started_at = datetime.now(UTC)
    started = time.monotonic()
    exit_code = None
    fail = False

    with tempfile.TemporaryFile(dir=TMP_ROOT) as log:
        try:
            with tempfile.TemporaryDirectory(dir=TMP_ROOT) as directory:
                archive_path = Path(directory) / "download.crate"
                source_dir = Path(directory) / "source"
                with (
                    http_get(download_url) as response,
                    archive_path.open("wb") as file,
                ):
                    shutil.copyfileobj(response, file)

                with tarfile.open(archive_path, "r:gz") as archive:
                    archive.extractall(source_dir, filter="data")
                crate_dir = source_dir / package

                exit_code = subprocess.run(
                    CHECK_COMMAND, cwd=crate_dir, stdout=log, stderr=subprocess.STDOUT
                ).returncode
        except Exception as error:
            fail = True
            log.write(f"\n  (Python): {error}\n".encode("utf-8"))

        header = (
            f"Exit code: {exit_code}\n"
            f"Crate: {name}\n"
            f"Version: {version}\n"
            f"Rank: {rank}\n"
            f"Downloads: {downloads}\n"
            f"Started at: {started_at.isoformat()}\n"
            f"Elapsed seconds: {time.monotonic() - started:.2f}\n"
            f"Command: {' '.join(CHECK_COMMAND)}\n"
            f"Archive: {download_url}\n"
            "\n--- Log ---\n"
        )
        log.seek(0)
        with tempfile.NamedTemporaryFile(
            dir=RESULTS_DIR, delete_on_close=False
        ) as report:
            report.write(header.encode("utf-8"))
            shutil.copyfileobj(log, report)
            report.close()
            Path(report.name).replace(report_path)

    print(f"  {package}:  {report_path}", flush=True)
    return not fail


def main() -> int:
    try:
        crates = top_crates()
    except Exception as error:
        print(f"crate get: {error}", file=sys.stderr)
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    passed = 0
    for rank, crate in enumerate(crates, start=1):
        print(f"[{rank}/{len(crates)}] {crate.name} {crate.version}", flush=True)
        passed += check_crate(rank, crate.name, crate.version, crate.downloads)
    print(f"{passed}/{len(crates)} checks passed (requested {TOP_N}).")
    return 0 if passed == TOP_N else 1


if __name__ == "__main__":
    sys.exit(main())
