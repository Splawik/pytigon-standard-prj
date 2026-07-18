from pytigon_lib.schviews.viewtools import (
    dict_to_template,
    dict_to_odf,
    dict_to_pdf,
    dict_to_json,
    dict_to_xml,
    dict_to_ooxml,
    dict_to_txt,
    dict_to_hdoc,
)


from tables_demo.models import Example1Computer


@dict_to_odf("views_demo/v_odf_example.ods")
def odf_example(request, **argv):
    """
    Generate an ODF document from the v_odf_example.ods template.

    Fills the template with a name and description string via the
    ``@dict_to_odf`` decorator.
    """

    return {"name": "odf test", "description": "Hello!"}


@dict_to_pdf("views_demo/v_pdf_example_pdf.html")
def pdf_example(request, **argv):
    """
    Generate a PDF from the v_pdf_example_pdf.html template.

    Renders the HTML template with a name and description dict via
    ``@dict_to_pdf``, producing a downloadable PDF.
    """

    return {"name": "pdf test", "description": "Hello!"}


@dict_to_json
def json_example(request, **argv):
    """
    Return a sample JSON response.

    Serializes a name/description dict to JSON via ``@dict_to_json``.
    """

    return {"name": "json test", "description": "Hello!"}


@dict_to_xml
def xml_example(request, **argv):
    """
    Return all Example1Computer objects serialized as XML.

    Queries the full table and serializes the queryset via
    ``@dict_to_xml``.
    """

    return Example1Computer.objects.all()


@dict_to_ooxml("views_demo/v_xlsx_example.xlsx")
def xlsx_example(request, **argv):
    """
    Generate an Excel (XLSX) file from the v_xlsx_example.xlsx template.

    Fills the template with name, description, and a numeric value via
    ``@dict_to_ooxml``.
    """

    return {"name": "xlsx test", "description": "Hello!", "x": 1.4}


@dict_to_txt("views_demo/v_txt_example_txt.html")
def txt_example(request, **argv):
    """
    Generate a plain-text response from the v_txt_example_txt.html template.

    Renders the template as plain text with a name/description dict via
    ``@dict_to_txt``.
    """

    return {"name": "txt test", "description": "Hello!"}


@dict_to_template("views_demo/v_template_example.html")
def template_example(request, **argv):
    """
    Render the standard template example page.

    Passes a name/description dict to v_template_example.html via
    ``@dict_to_template``.
    """

    return {"name": "template test", "description": "Hello!"}


@dict_to_hdoc("views_demo/v_hdoc_example_hdoc.html")
def hdoc_example(request, **argv):
    """
    Generate an HDOC output from the v_hdoc_example_hdoc.html template.

    Renders the template as HDOC format with a name/description dict via
    ``@dict_to_hdoc``.
    """

    return {"name": "txt test", "description": "Hello!"}


@dict_to_template("views_demo/v_plotly_example.html")
def plotly_example(request, **argv):
    """
    Create a Plotly scatter plot and return its HTML fragment.

    Generates random data for a scatter plot via plotly.graph_objects,
    renders the figure as standalone HTML, and passes it as
    ``plotly_content`` to the v_plotly_example.html template.
    """

    import plotly.graph_objects as go
    import numpy as np
    from io import StringIO

    np.random.seed(1)

    N = 100
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    sz = np.random.rand(N) * 30

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=go.scatter.Marker(
                size=sz, color=colors, opacity=0.6, colorscale="Viridis"
            ),
        )
    )
    buf = StringIO()
    fig.write_html(buf, include_plotlyjs=False, full_html=False)
    return {"plotly_content": buf.getvalue()}


@dict_to_template("views_demo/v_plotly_export_example.html")
def plotly_export_example(request, **argv):
    """
    Create and export Plotly figures as inline SVG.

    Generates an iris dataset scatter plot and a European population pie
    chart via plotly.express, exports both as SVG bytes, and passes them
    as ``img1_svg``/``img2_svg`` to the template.
    """

    from io import BytesIO
    import plotly.express as px

    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

    x1 = BytesIO()
    fig.write_image(x1, format="svg")

    df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
    df.loc[df["pop"] < 2.0e6, "country"] = "Other countries"
    fig = px.pie(
        df, values="pop", names="country", title="Population of European continent"
    )

    x2 = BytesIO()
    fig.write_image(x2, format="svg")

    return {"img1_svg": x1.getvalue(), "img2_svg": x2.getvalue()}
