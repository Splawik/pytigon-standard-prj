var BASE_PATH, TAG, TEMPLATE, comp, css_libs, height, init, js_libs, stub1_context, stub2_err, width;
TAG = "ptig-newschool";
TEMPLATE = '        <div class=\"container-fluid\">\n' +
    '                <table width=\"100%\" height=\"100%\">\n' +
    '                        <tr>\n' +
    '                                <td>\n' +
    '                                        <div class=\"spreadsheet\"></div>\n' +
    '                                </td>\n' +
    '                                <td class=\"button\" style=\"vertical-align:top;height:100%;\">\n' +
    '                                        <button type=\"button\" class=\"btn btn-primary\" style=\"width:100%;height: calc( 100% - 30px );\" data-bind=\"disabled:!changed;onclick:on_save\">\n' +
    '                                                +\n' +
    '                                        </button>\n' +
    '                                </td>\n' +
    '                                <td width=\"100%\"></td>\n' +
    '                        </tr>\n' +
    '                </table>\n' +
    '        </div>\n' +
    '\n' +
    '';
BASE_PATH = window.BASE_PATH + "static/vanillajs_plugins";
js_libs = [BASE_PATH + "/jexcel/jexcel.js", BASE_PATH + "/jsuites/jsuites.js"];
css_libs = [BASE_PATH + "/jsuites/jsuites.css", BASE_PATH + "/jexcel/jexcel.css"];
stub1_context = (new DefineWebComponent(TAG, false, js_libs, css_libs));
comp = stub1_context.__enter__();
try {
    width = function flx_width (component, old_value, new_value) {
        component.root.style.width = new_value;
        return null;
    };

    height = function flx_height (component, old_value, new_value) {
        component.root.style.height = new_value;
        return null;
    };

    comp.options["attributes"] = ({width: width, height: height});
    comp.options["template"] = TEMPLATE;
    init = function flx_init (component) {
        var base_elem, columns, data, on_save, state;
        columns = [({type: "text", title: "Nazwisko", width: 240}), ({type: "text", title: "Imie", width: 240}), ({type: "text", title: "Email", width: 128}), ({type: "numeric", title: "Rabat", width: 120, mask: "# ##.00", decimal: "."})];
        data = [];
        base_elem = component.querySelector(".spreadsheet");
        component.jtable = jexcel(base_elem, ({data: data, columns: columns, minDimensions: [3, 1], allowInsertColumn: false, tableWidth: "100%"}));
        on_save = (function flx_on_save (event) {
            var _on_complete, data, href;
            if (_pyfunc_truthy(component.hasAttribute("href"))) {
                href = component.getAttribute("href");
                data = ({action: "insert_rows", table: component.jtable.getData()});
                _on_complete = (function flx__on_complete (data) {
                    refresh_ajax_frame(component, "table", data);
                    component.jtable.setData([]);
                    ((jQuery(component.closest(".collapse"))).collapse)("hide");
                    return null;
                }).bind(this);

                ajax_json(href, data, _on_complete);
            }
            return null;
        }).bind(this);

        state = ({on_save: on_save, changed: true});
        component.set_state(state);
        return null;
    };

    comp.options["init"] = init;
} catch(err_0)  { stub2_err=err_0;
} finally {
    if (stub2_err) { if (!stub1_context.__exit__(stub2_err.name || "error", stub2_err, null)) { throw stub2_err; }
    } else { stub1_context.__exit__(null, null, null); }
}