# Faça um sistema que receba o valor do salário e da despesa e mostre o valor
# do saldo, ou seja, a diferença entre o salário e a despesa.

if __name__ == "__main__":
    try:
        salario = float(input("Digite o valor do salário: "))
        despesa = float(input("Digite o valor da despesa: "))
    except ValueError:
        print("Por favor, digite um valor numérico válido.")
    else:
        resultado = salario - despesa
        print(f"O valor do saldo é: {resultado:.2f}")

    if resultado > 0:
        print("Parabéns! Você tem um saldo positivo.")
    elif resultado < 0:
        print("Cuidado! Você tem um saldo negativo.")
    else:
        print("Você está no zero a zero, sem saldo positivo ou negativo.")
