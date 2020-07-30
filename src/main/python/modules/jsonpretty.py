#!/usr/bin/python
# coding=utf8

import sys
import json


def check_caret(data):
    if data.startswith("["):
        if data.endswith("]"):
            return data
        else:
            return data[0: data.rfind("]") + 1]
    elif data.startswith("{"):
        if data.endswith("}"):
            return data
        else:
            return data[0: data.rfind("}") + 1]
    else:
        data = data[1:]
        return check_caret(data)


def pretty(data):
    return json.dumps(pretty_json(data), ensure_ascii=False, indent=4)


def pretty_json(data):
    if isinstance(data, str):
        data = replace(data)
        json_data = json.loads(data)
        return json_data
    else:
        return data


def replace(data):
    data = check_caret(data)
    return data


def extract(data, key):
    new_out = []
    if not key:
        return data
    for extr in key:
        for a in data:
            if extr in a:
                temp = a[extr]
                if temp != "":
                    try:
                        ss = pretty_json(temp)
                        ss = extract(ss, key)
                        a[extr] = ss
                    except Exception as ex:
                        print(ex)
                        a[extr] = temp

            new_out.append(a)

    return new_out


def read_file(path):
    f = open(path, "r", encoding="utf-8")
    out = f.read()
    f.close()
    print(path + ", length: " + str(len(out)))

    out = pretty(out)

    if out != "":
        fout = open(path, "w", encoding="utf-8")
        fout.write(out)
        fout.close()


def main():
    path = sys.argv[1]
    read_file(path)


if __name__ == "__main__":
    main()
