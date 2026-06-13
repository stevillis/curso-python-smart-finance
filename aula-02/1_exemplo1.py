if __name__ == "__main__":
    idade = int(input("Digite a idade: "))
    if idade < 18:
        print("Menor de idade")
    elif idade < 65:
        print("Adulto")
    else:
        print("Idoso")
