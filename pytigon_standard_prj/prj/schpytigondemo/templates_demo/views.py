from pytigon_lib.schviews.viewtools import dict_to_template


@dict_to_template("templates_demo/v_excel_report.html")
def excel_report(request, **argv):
    """
    Generate an Excel (OOXML) report with sample data.

    Returns a context with 9,999 numbered title rows, XLSX doc type,
    and sheet names ``abc``/``def`` for demonstrating Excel report
    generation via the dict_to_template pipeline.
    """

    object_list = [(f"title {i}", i) for i in range(1, 10000)]

    return {
        "doc_type": "xlsx",
        "object_list": object_list,
        "sheet_names": ["abc", "def"],
        "sheet_name": "abc",
    }


@dict_to_template("templates_demo/v_odf_report.html")
def odf_report(request, **argv):
    """
    Generate an ODF spreadsheet report with sample data.

    Returns a context with 9,999 numbered title rows, ODS doc type,
    and sheet names ``abc``/``def`` for demonstrating OpenDocument
    spreadsheet generation via the dict_to_template pipeline.
    """

    object_list = [(f"title {i}", i) for i in range(1, 10000)]

    return {
        "doc_type": "ods",
        "object_list": object_list,
        "sheet_names": ["abc", "def"],
        "sheet_name": "abc",
    }
