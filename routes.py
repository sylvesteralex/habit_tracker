from flask import Blueprint, current_app, render_template, request, redirect, url_for
import datetime as dt
import uuid
# from collections import defaultdict


pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")

# habits = ["habit 1", "habit 2", "habit 3"]
# completions = defaultdict(list)


@pages.context_processor
def add_calc_date_range():
    def date_range(start: dt.datetime):
    # def date_range(start: dt.date):
        dates = [start + dt.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"dates": date_range}


def today_at_midnight():
    today = dt.datetime.today()

    return dt.datetime(today.year, today.month, today.day)


@pages.route("/")
def home():
    date_str = request.args.get("date")
    if date_str:
        # selected_date = dt.date.fromisoformat(date_str)
        selected_date = dt.datetime.fromisoformat(date_str)
    else:
        # selected_date = dt.date.today()
        selected_date = today_at_midnight()

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [ habit["habit"] for habit in current_app.db.completions.find({"date": selected_date}) ]

    return render_template(
        "index.html",
        title="Habit Tracker",
        selected_date=selected_date,
        # completions=completions[selected_date],
        completions=completions,
        habits=habits_on_date,
        today=today_at_midnight()
    )

@pages.route("/add", methods=["POST", "GET"])
def add_habit():
    today = today_at_midnight()

    if request.method == "POST":
        # new_habit = request.form.get("addHabit")
        # habits.append(new_habit)
        current_app.db.habits.insert_one({
            "_id": uuid.uuid4().hex,
            "added": today,
            "name": request.form.get("habitName")
        })

        return redirect(url_for("habits.home"))

    return render_template(
        "add_habit.html",
        title="Add a habit",
        selected_date=today
    )


@pages.post("/complete")
def complete():
    date_string = request.form.get("date")
    # habit = request.form.get("habitName")
    habit = request.form.get("habitId")
    date = dt.datetime.fromisoformat(date_string)
    # completions[date].append(habit)
    current_app.db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for("habits.home", date=date))

