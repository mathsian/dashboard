from dash.dependencies import Input, Output, State
import datetime
import data


def register_callbacks(app):
    @app.callback(
        [
            Output("dialog-kudos-confirm", "message"),
            Output("dialog-kudos-confirm", "displayed"),
        ],
        [Input("input-kudos-description", "n_submit")],
        [
            State("input-kudos-description", "value"),
            State("dropdown-kudos-value", "value"),
            State("dropdown-kudos-points", "value"),
            State("store-student", "data"),
        ],
    )
    def confirm_kudos(n_submit, description, value, points, store_student):
        if store_student:
            if n_submit:
                msg = f"Award {points} {value} kudos to {store_student} for {description}?"
                return msg, True
            else:
                return "Cancelled", False
        else:
            return "No student selected", False

    @app.callback(
        Output("div-kudos-message", "children"),
        [
            Input("dialog-kudos-confirm", "submit_n_clicks"),
            Input("store-student", "data"),
        ],
        [
            State("input-kudos-description", "value"),
            State("dropdown-kudos-value", "value"),
            State("dropdown-kudos-points", "value"),
        ],
    )
    def submit_kudos(clicks, store_student, description, value, points):
        if clicks and store_student:
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            doc = {
                "type": "kudos",
                "student_id": store_student["student_id"],
                "ada_value": value,
                "points": points,
                "description": description,
                "date": date,
            }
            data.save_docs([doc])
            return f"Kudos submitted to {store_student.get('given_name')}"
        elif store_student:
            return f"Award kudos to {store_student.get('given_name')}"
        else:
            return "Select student to award kudos"
