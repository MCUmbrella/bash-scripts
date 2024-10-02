#!/usr/bin/python3

import os
import pandas as pd
import json
import argparse


def float_range(mini, maxi):
    """ https://stackoverflow.com/a/64259328 """
    def float_range_checker(arg):
        try:
            f = float(arg)
        except ValueError:
            raise argparse.ArgumentTypeError("must be a floating point number")
        if f < mini or f > maxi:
            raise argparse.ArgumentTypeError("must be in range [" + str(mini) + " .. " + str(maxi)+"]")
        return f
    return float_range_checker

# 处理命令行参数
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("-a", "--avg", action="store_true", dest="flAvg", help="以每个文件数据的平均值绘制图表")
parser.add_argument("-c", "--cli", action="store_true", dest="flCli", help="在终端绘制图表。最好配合“-a”使用")
parser.add_argument("-d", "--data", action="store", dest="dataDir", default="data", metavar="<path>", help="指定存放json数据的文件夹。默认为“data”")
parser.add_argument("-n", "--miner", action="store", dest="minerName", default="global", metavar="<name>", help="指定矿工名。默认为“global”")
parser.add_argument("--clean", action="store_true", dest="flClean", help="丢弃离群值（使用IQR方法）")
parser.add_argument("--quantile", type=float_range(0, 0.5), action="store", dest="quantile", default=0.25, metavar="<number>", help="更改IQR使用的分位。默认为0.25，必须是小于0.5的正数")
args: argparse.Namespace = parser.parse_args()

if args.flCli:
    import plotext as plt
    import datetime
else:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    from matplotlib.dates import DateFormatter

dataDir: str = args.dataDir # 存放json数据的文件夹，默认为“data”
minerName: str = args.minerName # 矿工名，默认为“global”

# 获取data目录下所有满足条件的文件名
print(f"正在从 \"{dataDir}\" 导入 \"{minerName}\" 的数据")
files: list
try:
    files = sorted([file for file in os.listdir(dataDir) if file.endswith(".json")])
except BaseException as e:
    print("失败:", e)
    exit(-1)

# 初始化一个空的DataFrame来存储所有数据
data: pd.DataFrame = pd.DataFrame()

# 读取每个文件并将数据合并到data
fileCnt: int = 0 # 导入文件的个数
for fileName in files:
    with open(os.path.join(dataDir, fileName), "r") as file:
        print(f"导入 {fileName} ... ", end="")
        try:
            j: json = json.load(file)
            df: pd.DataFrame = pd.DataFrame(j[minerName])
            if args.flAvg:
                df["ts"] = df["ts"].mean()
                df["hs"] = df["hs"].mean()
                df["hs2"] = df["hs2"].mean()
            data = pd.concat([data, df])
            print("成功")
            fileCnt += 1
        except BaseException as e:
            print("失败:", e)

print(f"已导入 {fileCnt} 个文件")

if data.size == 0:
    print("未发现有效数据 (矿工名、数据位置或数据格式是否正确?)")
    exit()

print("正在排序和去重")
dataSizeOld: int = len(data)
data = data.sort_values(by="ts")
data.drop_duplicates(keep="first", inplace=True)
print(f"已丢弃 {dataSizeOld - len(data)} 条重复数据")

if args.flClean:
    print("正在清理数据")
    quantileLower = args.quantile
    quantileUpper = 1 - quantileLower

    q1Raw: float = data["hs"].quantile(quantileLower)
    q3Raw: float = data["hs"].quantile(quantileUpper)
    iqrRaw: float = q3Raw - q1Raw
    rawUpperBound: float = q3Raw + 1.5 * iqrRaw
    rawLowerBound: float = max(0, q1Raw - 1.5 * iqrRaw)
    q1Pay: float = data["hs2"].quantile(quantileLower)
    q3Pay: float = data["hs2"].quantile(quantileUpper)
    iqrPay: float = q3Pay - q1Pay
    payUpperBound: float = q3Pay + 1.5 * iqrPay
    payLowerBound: float = max(0, q1Pay - 1.5 * iqrPay)

    dataSizeHighOutliersOld: int = len(data)
    data = data[(data["hs"] <= rawUpperBound) & (data["hs2"] <= payUpperBound)]
    dataSizeHighOutliersNew: int = len(data)

    dataSizeLowOutliersOld: int = len(data)
    data = data[(data["hs"] >= rawLowerBound) & (data["hs2"] >= payLowerBound)]
    dataSizeLowOutliersNew: int = len(data)

    print(f"已丢弃 {dataSizeHighOutliersOld - dataSizeLowOutliersNew} 条极端数据（{dataSizeHighOutliersOld - dataSizeHighOutliersNew} 过高 + {dataSizeLowOutliersOld - dataSizeLowOutliersNew} 过低，分位比例：{args.quantile}）")

print("平均RAW算力:", data["hs"].mean())
print("平均PAY算力:", data["hs2"].mean())

plt.title(f"Mining history: {minerName}")
plt.xlabel("Time")
plt.ylabel("Hashrate")
plt.grid()
if args.flCli:
    print("正在输出图表到终端")
    data["ts"] = data["ts"].apply(lambda timestamp: datetime.datetime.fromtimestamp(timestamp / 1000, datetime.timezone.utc).astimezone().strftime("%d/%m/%Y"))
    plt.plot(data["ts"], data["hs"], label="RAW", color="red")
    plt.plot(data["ts"], data["hs2"], label="PAY", color="blue")
else:
    print("正在绘制图表")
    data["ts"] = pd.to_datetime(data["ts"], unit="ms").dt.tz_localize("UTC")
    pltMarkerStyle: str = "o" if args.flAvg else ""
    plt.plot(data["ts"], data["hs"], label="RAW", color="red", marker=pltMarkerStyle, markersize=2)
    plt.plot(data["ts"], data["hs2"], label="PAY", color="blue", marker=pltMarkerStyle, markersize=2)
    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Microsoft YaHei", "Noto Sans CJK", "DejaVu Sans"]
    rcParams["timezone"] = "Asia/Shanghai"
    plt.gca().xaxis.set_major_formatter(DateFormatter("%y-%m-%d" if args.flAvg else "%m-%d %H:%M"))
    plt.gca().set_xlim(xmin=min(data["ts"]))
    plt.gca().set_xlim(xmax=max(data["ts"]))
    plt.gca().set_ylim(ymin=0)
    plt.tight_layout()
    plt.legend()
plt.show()
