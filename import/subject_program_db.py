def exec_pc(t: dict):
    pc = []

    if t["age"] < 40:
        pc.append(("age", "<", 40))
        if t["zip_code"] < 50000:
            pc.append(("zip_code", "<", 50000))
            if t["disease"] == "Cancer":
                # age < 40 and zipcode < 50000 and disease == Cancer
                pc.append(("disease", "==", "Cancer"))
            else:
                # age < 40 and zipcode < 50000 and disease != Cancer
                pc.append(("disease", "!=", "Cancer"))
        elif t["zip_code"] >= 70000:
            pc.append(("zip_code", ">=", 70000))
            if t["disease"] == "Anorexia":
                # age < 40 and zipcode >= 70000 and disease == Anorexia
                pc.append(("disease", "==", "Anorexia"))
            else:
                # age < 40 and zipcode >= 70000 and disease != Anorexia
                pc.append(("disease", "!=", "Anorexia"))
        else:
            pc.append(("zip_code", ">=", 50000))
            pc.append(("zip_code", "<", 70000))
            if t["disease"] == "AIDS":
                # age < 40 and 50000 <= zipcode < 70000 and disease == AIDS
                pc.append(("disease", "==", "AIDS"))
            else:
                # age < 40 and 50000 <= zipcode < 70000 and disease != AIDS
                pc.append(("disease", "!=", "AIDS"))
    else:
        pc.append(("age", ">=", 40))
        if t["zip_code"] < 40000:
            pc.append(("zip_code", "<", 40000))
            if t["disease"] == "Heart disease":
                # age >= 40 and zipcode < 40000 and disease == Heart disease
                pc.append(("disease", "==", "Heart disease"))
            else:
                # age >= 40 and zipcode < 40000 and disease != Heart disease
                pc.append(("disease", "!=", "Heart disease"))
        elif t["zip_code"] >= 80000:
            pc.append(("zip_code", ">", 80000))
            if t["disease"] == "Alzheimer's disease":
                # age >= 40 and zipcode >= 80000 and disease == Alzheimer's disease
                pc.append(("disease", "==", "Alzheimer's disease"))
            else:
                # age >= 40 and zipcode >= 80000 and disease != Alzheimer's disease
                pc.append(("disease", "!=", "Alzheimer's disease"))
        else:
            pc.append(("zip_code", ">=", 40000))
            pc.append(("zip_code", "<=", 80000))
            if t["disease"] == "Autism":
                # age >= 40 and 40000 <= zipcode <= 80000 and disease == Autism
                pc.append(("disease", "==", "Autism"))
            else:
                # age >= 40 and 40000 <= zipcode <= 80000 and disease != Autism
                pc.append(("disease", "!=", "Autism"))

    return pc
