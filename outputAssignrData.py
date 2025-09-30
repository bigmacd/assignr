def printPaymentInfo(paymentDetails: dict) -> dict:
    retVal = {}
    totalAllAssignors = 0.0
    for assignor in paymentDetails:
        totalForAssignor = 0.0
        assignorName = paymentDetails[assignor][0]['name'] if len(paymentDetails[assignor]) > 0 else "Unknown"
        retVal[assignorName] = 0.0
        print(f"Assignor {assignorName} ({assignor}) has {len(paymentDetails[assignor])} payments")
        for payment in paymentDetails[assignor]:
            print(f"  {payment['date']} {payment['name']} amount {payment['amount']} paid {payment['amount_paid']} {payment['description']} ")
            totalForAssignor += payment['amount_paid']
        print(f"Total for {assignorName} is {totalForAssignor}")
        totalAllAssignors += totalForAssignor
        retVal[assignorName] = totalForAssignor
    print(f"Total for all assignors is {totalAllAssignors}")

    return retVal


def printGameSummary(gameDetails: dict) -> dict:
    retVal = {}
    totalAllAssignors = 0.0
    for assignor in gameDetails:
        totalForAssignor = 0.0
        assignorName = gameDetails[assignor][0]['site']['name']
        # Hack, here is Tarey again not knowing what she is doing
        if assignorName == "TSH Referee Assigning Services LLC":
            assignorName = "TSH Assignor Services LLC"
        retVal[assignorName] = 0.0
        print(f"Assignor {assignorName} ({assignor}) has {len(gameDetails[assignor])} games")
        for game in gameDetails[assignor]:
            print(f"\tGame {game['gameid']} at {game['venue']['name']} with assignments:")
            for assignment in game['assignments']:
                if '_embedded' not in assignment:
                    continue
                official = assignment['_embedded']['official']
                if official['first_name'] == "Martin" and official['last_name'] == "Cooley":
                    totalForAssignor += assignment['_embedded']['fees'][0]['value']
                    print(f"\t\t{assignment['position']} - {official['first_name']} {official['last_name']}")
        print(f"Total for {assignorName} is {totalForAssignor}")
        retVal[assignorName] = totalForAssignor
        totalAllAssignors += totalForAssignor
    print(f"Total for all assignors is {totalAllAssignors}")

    return retVal

