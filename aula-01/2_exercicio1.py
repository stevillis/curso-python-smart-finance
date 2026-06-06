# Faça um sistema que receba o valor do salário e da despesa e mostre o valor
# do saldo, ou seja, a diferença entre o salário e a despesa.

if __name__ == "__main__":
    salario = float(input("Digite o valor do salário: "))
    despesa = float(input("Digite o valor da despesa: "))
    print(f"O valor do saldo é: {salario - despesa:.2f}")
