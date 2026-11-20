fn original() {
    let haystack = "heystack";
    let mut input = aho_corasick::Input::new(haystack);
    let inner_haystack = input.haystack();
    input.set_span(2..4);
    println!("{inner_haystack:?}");
}

fn edited() {
    let haystack = "heystack";
    let mut input = aho_corasick_edited::Input::new(haystack);
    let inner_haystack = input.haystack();
    input.set_span(2..4);
    println!("{inner_haystack:?}");
}
