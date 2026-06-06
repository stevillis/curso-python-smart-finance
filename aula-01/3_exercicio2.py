# Faça um sistema que receba o valor do salário e da despesa e mostre o valor
# do saldo, ou seja, a diferença entre o salário e a despesa.

if __name__ == "__main__":
    try:
        salario = float(input("Digite o valor do salário: "))
        despesa = float(input("Digite o valor da despesa: "))
        print(f"O valor do saldo é: {salario - despesa:.2f}")
    except ValueError:
        print("Por favor, digite um valor numérico válido.")
    else:
        print("Cálculo realizado com sucesso.")

    print("Linha sempre executada.")
