if __name__ == "__main__":
    while True:
        opcao = input(
            "Digite 'q' para encerrar ou qualquer outra coisa para continuar: "
        )
        if opcao == "q":
            break
        elif opcao == "pular":
            continue

        print("Você escolheu continuar!")
