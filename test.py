def test(a):
    try:
        if a == 1:
            raise Exception
        return a
    except Exception:
        print("error")
    finally:
        print("finally")


print(test(2))
