if __name__ == "__main__":
    transacoes = ["Luz", "Água", "Internet", "Aluguel", "Supermercado"]
    precos = [100, 50, 150, 1200, 500]
    datas = ["2024-01-10", "2024-01-15", "2024-01-20", "2024-01-25", "2024-01-30"]

    while True:
        print("Olá! Eu sou seu Assistente Financeiro.")
        print("\n", "=" * 30)

        print("1. Visualizar o extrato da conta")
        print("2. Adicionar nova transação")
        print("3. Ver total de despesas")

        print("\n", "=" * 30)

        opcao = (
            input("Escolha uma opção (1, 2, 3) ou 'q' para encerrar: ").strip().lower()
        )
        if opcao == "q":
            print("Encerrando o Assistente Financeiro. Até logo!")
            break
        elif opcao == "1":
            print("1. Visualizar o extrato da conta")
            print("Exibindo o extrato da conta...")
            for transacao, preco, data in zip(transacoes, precos, datas):
                print(f"Transação: {transacao}, Preço: {preco}, Data: {data}")
        elif opcao == "2":
            print("2. Adicionar nova transação")
            nova_transacao = input("Digite o nome da nova transação: ")
            novo_preco = float(input("Digite o preço da nova transação: "))
            nova_data = input("Digite a data da nova transação (YYYY-MM-DD): ")

            transacoes.append(nova_transacao)
            precos.append(novo_preco)
            datas.append(nova_data)

            print("Nova transação adicionada com sucesso!")
        elif opcao == "3":
            print("Calculando total de despesas...")
            total_despesas = sum(precos)
            print(f"Total de despesas: {total_despesas}")
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

        print("\n\n")
