import base64
import io

from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required

from .. import stock_client
from ..forms import stockWatchForm, SearchForm
from ..models import User, watchedStock
from ..utils import current_time

stocks = Blueprint("stocks", __name__)

""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ View functions ************ """


@stocks.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("stocks.stock_detail", stock_id=form.search_query.data))

    return render_template("index.html", form=form)


@stocks.route("/stocks/<stock_id>", methods=["GET"])
def stock_detail(stock_id):
    try:
        result = stock_client.get_stock_details(stock_id)
    except ValueError as e:
        return render_template(
            "stock_detail.html",
            error_msg="We couldn't find that stock symbol. Please enter a valid ticker symbol.<br><a href='https://stockanalysis.com/stocks/' target='_blank' rel='noopener noreferrer' style='color: blue; text-decoration: underline;'>Supported Stock Symbols</a>",
        )

    everyonesWatchedStocks = watchedStock.objects(name=result.name)

    return render_template(
        "stock_detail.html", form=stockWatchForm(), stock=result, watchers=everyonesWatchedStocks
    )


@stocks.route("/stocks/<stock_id>/watch", methods=["POST"])
@login_required
def watch_stock(stock_id):
    try:
        result = stock_client.get_stock_details(stock_id)
    except ValueError:
        return redirect(url_for("stocks.stock_detail", stock_id=stock_id))

    form = stockWatchForm()
    if not form.validate_on_submit():
        return redirect(url_for("stocks.stock_detail", stock_id=stock_id))

    image_data = None
    if current_user.profile_pic:
        bytes_im = io.BytesIO(current_user.profile_pic.read())
        image_data = base64.b64encode(bytes_im.getvalue()).decode()

    stock = watchedStock(
        watcher=current_user._get_current_object(),
        date=current_time(),
        name=result.name,
        symbol=result.symbol,
        high=result.high,
        low=result.low,
        image=image_data,
    )
    stock.save()

    return redirect(url_for("stocks.stock_detail", stock_id=stock_id))


@stocks.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()

    if not user:
        error_msg = f"User '{username}' not found."
        return render_template("user_detail.html", error=error_msg)

    watchedStocks = watchedStock.objects(watcher=user)

    profile_pic = get_b64_img(user.username) if user.profile_pic else None

    return render_template(
        "user_detail.html",
        user=user,
        watchedStocks=watchedStocks,
        profile_pic=profile_pic,
        error=None
    )
