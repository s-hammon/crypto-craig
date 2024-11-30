from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


# Import data retrieved from database; return a scatter plot
def coin_scatter_plot(**kwargs):
    # # Import data from database
    coin = kwargs.pop("coin")
    prices = kwargs.pop("prices")
    time = kwargs.pop("time")

    x_values = mdates.date2num(time)

    _, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_values, prices, color="b")

    locator = mdates.AutoDateLocator(maxticks=5)
    formatter = mdates.AutoDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(dollar_format))

    plt.xticks(rotation=45)
    plt.title(f"{coin} Price")
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)

    return img


def dollar_format(x: int, pos):
    if x >= 10_000:
        return f"${x/1_000:,.0f}k"
    elif x >= 1:
        return f"${x:,.0f}"
    elif x >= 0.01:
        return f"${x:,.2f}"
    else:
        return f"${x:,.6f}"
