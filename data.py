import requests
import os
import csv
import sqlite3
import pandas as pd


# ---------下載資料---------#
def __download_credit_data() -> csv:
    area = [
        "KLC",
        "TPE",
        "NTP",
        "TYC",
        "HCC",
        "HCH",
        "MLH",
        "TCC",
        "CHH",
        "NTH",
        "YUH",
        "CYC",
        "CYH",
        "TNC",
        "KHC",
        "PTH",
        "TTH",
        "HLH",
        "YIH",
        "PHH",
        "KMH",
        "LCH",
        "X1",
        "LCSUM",
        "MCT",
        "LOC",
    ]
    area_code = {
        "63000000": "臺北市",
        "64000000": "高雄市",
        "65000000": "新北市",
        "66000000": "臺中市",
        "67000000": "臺南市",
        "68000000": "桃園市",
        "10002000": "宜蘭縣",
        "10004000": "新竹縣",
        "10005000": "苗栗縣",
        "10007000": "彰化縣",
        "10008000": "南投縣",
        "10009000": "雲林縣",
        "10010000": "嘉義縣",
        "10020000": "嘉義市",
        "10013000": "屏東縣",
        "10014000": "臺東縣",
        "10015000": "花蓮縣",
        "10016000": "澎湖縣",
        "10017000": "基隆市",
        "10018000": "新竹市",
        "9020000": "金門縣",
        "9007000": "連江縣",
    }
    industry = ["FD", "CT", "LG", "TR", "EE", "DP", "X2", "OT", " IDSUM", "ALL"]
    DataType = ["sex", "job", "incom", "education", "age"]
    sex = ["M", "F"]

    # 兩性消費
    for A in industry:
        for B in area:
            sex_url = (
                f"https://bas.nccc.com.tw/nccc-nop/OpenAPI/C01/sexconsumption/{B}/{A}"
            )
            response_sex = requests.request("GET", sex_url)
            if len(response_sex.text) == 0:
                continue
            with open(f"./datasource/sex/sex{B}_{A}.csv", "wb") as file:
                file.write(response_sex.content)
                file.close()
    print("性別消費資料讀取成功")

    # 各職業類別消費樣態資料
    for E in industry:
        for F in area:
            job_url = (
                f"https://bas.nccc.com.tw/nccc-nop/OpenAPI/C04/jobsconsumption/{F}/{E}"
            )
            response_job = requests.request("GET", job_url)
            if len(response_job.text) == 0:
                continue
            with open(f"./datasource/job/job{F}_{E}.csv", "wb") as file:
                file.write(response_job.content)
                file.close()
    print("職業類別消費資料讀取成功")

    # 各年收入族群消費樣態資料(V)
    for G in industry:
        for H in area:
            incom_url = f"https://bas.nccc.com.tw/nccc-nop/OpenAPI/C03/incomegroupsconsumption/{H}/{G}"
            response_incom = requests.request("GET", incom_url)
            if len(response_incom.text) == 0:
                continue
            with open(f"./datasource/incom/incom{H}_{G}.csv", "wb") as file:
                file.write(response_incom.content)
                file.close()
    print("收入類別消費資料讀取成功")

    # 各教育程度消費樣態資料(V)
    for I in industry:
        for J in area:
            education_url = f"https://bas.nccc.com.tw/nccc-nop/OpenAPI/C05/educationconsumption/{J}/{I}"
            response_education = requests.request("GET", education_url)
            if len(response_education.text) == 0:
                continue
            with open(f"./datasource/education/education{J}_{I}.csv", "wb") as file:
                file.write(response_education.content)
                file.close()
    print("教育程度資料讀取成功")

    # 兩性X各年齡層消費
    for A in industry:
        for B in area:
            for C in sex:
                age_url = f"https://bas.nccc.com.tw/nccc-nop/OpenAPI/C11/GenderAgeGroup/{B}/{A}/{C}"
                response_age = requests.request("GET", age_url)
                if len(response_age.text) == 0:
                    continue
                folder_path = "./datasource/age/"
                file_name = f"age{B}_{A}_{C}.csv"
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "wb") as file:
                    file.write(response_age.content)
                    file.close()
    print("年齡層消費資料讀取成功")

    # ---------合併csv---------#
    for item in DataType:
        path = f"./datasource/{item}/"
        csv_files = [file for file in os.listdir(path) if file.endswith(".csv")]
        merged_data = pd.DataFrame()
        for file in csv_files:
            file_path = os.path.join(path, file)
            data = pd.read_csv(file_path)
            merged_data = pd.concat([merged_data, data], ignore_index=True)
        merged_data.to_csv(f"{item}.csv", index=False)
        print(f"{item}.csv建立成功")

        with open(f"./{item}.csv", "r", encoding="UTF-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            fieldnames = csv_reader.fieldnames  # 取得csv的欄位名稱

            with open(f"./{item}_trans.csv", "w", encoding="utf-8", newline="") as file:
                # 新csv的欄位名稱
                # ["年","月"] -> 將年/月加在新欄位名稱的開頭
                # fieldnames[1:] -> 將其餘原始欄位名稱增加至新欄位名稱中
                new_fieldnames = ["年", "月"] + fieldnames[1:]
                csv_writer = csv.DictWriter(file, fieldnames=new_fieldnames)
                csv_writer.writeheader()

                for row in csv_reader:
                    # 使用get方法，如果找不到對應的鍵，就保持原來的值
                    row["地區"] = area_code.get(row["地區"], row["地區"])
                    # 將年月欄位分為年和月
                    year = row["年月"][:4]
                    month = row["年月"][4:]
                    # 將新欄位資料寫入新csv中
                    new_row = {"年": year, "月": month, "地區": row["地區"]}
                    new_row.update(row)  # 加入原有的資料
                    del new_row["年月"]  # 刪除原有的年月欄位
                    csv_writer.writerow(new_row)

                print(f"{item}_trans.csv建立成功")


# ---------輸入資料---------#
def csv_to_database(conn: sqlite3.Connection) -> None:
    DataType = ["sex", "job", "incom", "education", "age"]
    for item in DataType:
        file = f"./{item}_trans.csv"
        df = pd.read_csv(file)
        # 更改最後一個欄位名稱
        df.rename(columns={"信用卡交易金額[新台幣]": "信用卡金額"}, inplace=True)
        # 將Dataframe輸入至SQLite資料庫中
        df.to_sql(item, conn, if_exists="append", index=False)

    conn.close()


def main() -> None:
    __download_credit_data()
    conn = sqlite3.connect("creditcard.db")
    csv_to_database(conn)


if __name__ == "__main__":
    main()
