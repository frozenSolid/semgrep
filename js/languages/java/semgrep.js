//Provides: octs_create_parser_java
//Requires: wasm,lazy_instantiate_parser
function octs_create_parser_java() {
  return lazy_instantiate_parser(() => {
    const ptr = wasm._ts_parser_new();
    wasm._ts_parser_set_language(ptr, wasm._tree_sitter_java());
    return ptr;
  });
}
