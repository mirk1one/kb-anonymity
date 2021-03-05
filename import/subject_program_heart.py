def exec_pc(t: dict):
    pc = []

    if t["age"] < 40:
        pc.append(("age", "<", 40))
        if t["cp"] <= 1:
            pc.append(("cp", "<=", 1))
            if t["thalach"] < 120:
                # age < 40 and cp < 1 and thalach < 120
                pc.append(("thalach", "<", 120))
            elif t["thalach"] >= 165:
                # age < 40 and cp < 1 and thalach >= 165
                pc.append(("thalach", ">=", 165))
            else:
                # age < 40 and cp < 1 and 120 <= thalach < 165
                pc.append(("thalach", ">=", 120))
                pc.append(("thalach", "<", 165))
        else:
            pc.append(("cp", ">", 1))
            if t["thalach"] < 110:
                # age < 40 and cp > 1 and thalach < 110
                pc.append(("thalach", "<", 110))
            elif t["thalach"] > 155:
                # age < 40 and cp > 1 and thalach > 155
                pc.append(("thalach", ">", 155))
            else:
                # age < 40 and cp > 1 and 110 <= thalach <= 155
                pc.append(("thalach", ">=", 110))
                pc.append(("thalach", "<=", 155))
    else:
        pc.append(("age", ">=", 40))
        if t["cp"] <= 2:
            pc.append(("cp", "<=", 2))
            if t["thalach"] <= 100:
                # age >= 40 and cp <= 2 and thalach <= 100
                pc.append(("thalach", "<=", 100))
            elif t["thalach"] >= 140:
                # age >= 40 and cp <= 2 and thalach >= 140
                pc.append(("thalach", ">=", 140))
            else:
                # age >= 40 and cp <= 2 and 100 < thalach < 140
                pc.append(("thalach", ">", 100))
                pc.append(("thalach", "<", 140))
        else:
            pc.append(("cp", ">", 2))
            if t["thalach"] < 120:
                # age >= 40 and cp > 2 and thalach < 120
                pc.append(("thalach", "<", 120))
            elif t["thalach"] > 160:
                # age >= 40 and cp > 2 and thalach >= 160
                pc.append(("thalach", ">=", 160))
            else:
                # age >= 40 and cp > 2 and 120 <= thalach < 160
                pc.append(("thalach", ">=", 120))
                pc.append(("thalach", "<", 160))

    if t["sex"] == 0:
        pc.append(("sex", "==", 0))
        if t["fbs"] == 0:
            pc.append(("fbs", "==", 0))
            if t["chol"] < 220:
                pc.append(("chol", "<", 220))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and chol < 220 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and chol < 220 and exang == 1
                    pc.append(("exang", "==", 1))
            elif t["chol"] >= 300:
                pc.append(("chol", ">=", 300))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and chol >= 300 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and chol >= 300 and exang == 1
                    pc.append(("exang", "==", 1))
            else:
                pc.append(("chol", ">=", 220))
                pc.append(("chol", "<", 300))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and 220 <= chol < 300 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and 220 <= chol < 300 and exang == 1
                    pc.append(("exang", "==", 1))
        else:
            pc.append(("fbs", "==", 1))
            if t["chol"] <= 250:
                pc.append(("chol", "<=", 250))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and chol <= 250 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and chol <= 250 and exang == 1
                    pc.append(("exang", "==", 1))
            elif t["chol"] >= 295:
                pc.append(("chol", ">=", 295))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and chol >= 295 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and chol >= 295 and exang == 1
                    pc.append(("exang", "==", 1))
            else:
                pc.append(("chol", ">", 250))
                pc.append(("chol", "<", 295))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and 250 < chol < 295 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and 250 < chol < 295 and exang == 1
                    pc.append(("exang", "==", 1))
    else:
        pc.append(("sex", "==", 1))
        if t["fbs"] == 0:
            pc.append(("fbs", "==", 0))
            if t["chol"] <= 225:
                pc.append(("chol", "<=", 225))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and chol <= 225 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and chol <= 225 and exang == 1
                    pc.append(("exang", "==", 1))
            elif t["chol"] > 280:
                pc.append(("chol", ">", 280))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and chol > 280 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and chol > 280 and exang == 1
                    pc.append(("exang", "==", 1))
            else:
                pc.append(("chol", ">", 225))
                pc.append(("chol", "<=", 280))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 0 and 225 < chol <= 280 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 0 and 225 < chol <= 280 and exang == 1
                    pc.append(("exang", "==", 1))
        else:
            pc.append(("fbs", "==", 1))
            if t["chol"] <= 245:
                pc.append(("chol", "<=", 245))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and chol <= 245 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and chol <= 245 and exang == 1
                    pc.append(("exang", "==", 1))
            elif t["chol"] > 305:
                pc.append(("chol", ">", 305))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and chol > 305 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and chol > 305 and exang == 1
                    pc.append(("exang", "==", 1))
            else:
                pc.append(("chol", ">", 245))
                pc.append(("chol", "<=", 305))
                if t["exang"] == 0:
                    # sex == 0 and fbs == 1 and 245 < chol <= 305 and exang == 0
                    pc.append(("exang", "==", 0))
                else:
                    # sex == 0 and fbs == 1 and 245 < chol <= 305 and exang == 1
                    pc.append(("exang", "==", 1))

    if t["target"] == 0:
        pc.append(("target", "==", 0))
        if t["ca"] == 0:
            # target == 0 and ca == 0
            pc.append(("ca", "==", 0))
        elif t["ca"] == 1:
            # target == 0 and ca == 1
            pc.append(("ca", "==", 1))
        elif t["ca"] == 2:
            # target == 0 and ca == 2
            pc.append(("ca", "==", 2))
        else:
            # target == 0 and ca == 3
            pc.append(("ca", "==", 3))
    else:
        pc.append(("target", "==", 1))
        if t["ca"] == 0:
            # target == 1 and ca == 0
            pc.append(("ca", "==", 0))
        elif t["ca"] == 1:
            # target == 1 and ca == 1
            pc.append(("ca", "==", 1))
        elif t["ca"] == 2:
            # target == 1 and ca == 2
            pc.append(("ca", "==", 2))
        else:
            # target == 1 and ca == 3
            pc.append(("ca", "==", 3))

    return pc
