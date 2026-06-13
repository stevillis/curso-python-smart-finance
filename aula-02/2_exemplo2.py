if __name__ == "__main__":
    transacoes = ["Luz", "Água", "Internet", "Aluguel", "Supermercado"]
    precos = [100, 50, 150, 1200, 500]
    datas = ["2024-01-10", "2024-01-15", "2024-01-20", "2024-01-25", "2024-01-30"]

    print("Imprimindo transações")
    for transacao in transacoes:
        print(f"Transação: {transacao}")

    print("\nImprimindo preços")
    for preco in precos:
        print(f"Preço: {preco}")

    print("Imprimindo datas")
    for data in datas:
        print(f"Data: {data}")

    print("\nImprimindo itens correspondentes de cada lista usando zip:")
    for transacao, preco, data in zip(transacoes, precos, datas):
        print(f"Transação: {transacao}, Preço: {preco}, Data: {data}")

    print("\nImprimindo apenas a primeira transação, preço e data usando zip:")
    for transacao, preco, data in zip(transacoes[0:1], precos[0:1], datas[0:1]):
        print(f"Transação: {transacao}, Preço: {preco}, Data: {data}")

    print("\nImprimindo apenas a primeira transação de outra forma:")
    for posicao, transacao, preco, data in zip([0], transacoes, precos, datas):
        print(f"Transação: {transacao}, Preço: {preco}, Data: {data}")
