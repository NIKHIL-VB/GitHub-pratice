from flask import Flask, render_template, request

app = Flask(__name__)


plots = [
    {
        "id": 1,
        "name": "Green Valley Layout",
        "location": "Bengaluru",
        "size": "1200 sq.ft",
        "price": "₹18,00,000",
        "type": "Residential"
    },
    {
        "id": 2,
        "name": "Sunrise Residency",
        "location": "Mysuru",
        "size": "1500 sq.ft",
        "price": "₹22,00,000",
        "type": "Residential"
    },
    {
        "id": 3,
        "name": "Urban Heights",
        "location": "Hyderabad",
        "size": "1000 sq.ft",
        "price": "₹15,00,000",
        "type": "Commercial"
    }
]


@app.route("/")
def home():
    location = request.args.get("location", "").strip().lower()
    plot_type = request.args.get("plot_type", "").strip().lower()

    filtered_plots = []

    for plot in plots:
        location_matches = (
            location == ""
            or location in plot["location"].lower()
        )

        type_matches = (
            plot_type == ""
            or plot_type == plot["type"].lower()
        )

        if location_matches and type_matches:
            filtered_plots.append(plot)

    return render_template(
        "index.html",
        plots=filtered_plots,
        search_location=location,
        search_type=plot_type
    )


@app.route("/plot/<int:plot_id>")
def plot_details(plot_id):
    selected_plot = None

    for plot in plots:
        if plot["id"] == plot_id:
            selected_plot = plot
            break

    if selected_plot is None:
        return "Plot not found", 404

    return render_template(
        "plot_details.html",
        plot=selected_plot
    )


if __name__ == "__main__":
    app.run(debug=True)