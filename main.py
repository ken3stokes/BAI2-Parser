def parse_bai2(bai2_data):
    lines = bai2_data.strip().split('\n')

    parsed_data = {
        'header': {},
        'accounts': [],
        'control_totals': {}
    }

    account_data = None

    for line in lines:
        record_type = line[:2]

        # File Header
        if record_type == '01':
            parts = line.split(',')
            company_name = parts[1]
            bank_name = parts[2]
            date = parts[3]
            time = parts[4]
            parsed_data['header'] = {
                'company_name': company_name,
                'bank_name': bank_name,
                'date': date,
                'time': time
            }

        # Account Identifier
        elif record_type == '02':
            if account_data:
                parsed_data['accounts'].append(account_data)
            _, account_name, _, currency, _ = line.split(',')
            account_data = {
                'account_name': account_name,
                'currency': currency,
                'transactions': []
            }

        # Transaction Detail
        elif record_type == '16':
            parts = line.split(',')
            transaction_code = parts[1]
            amount = parts[2]
            transaction_date = parts[5]
            transaction_time = parts[6]
            description = parts[8]
            account_data['transactions'].append({
                'transaction_code': transaction_code,
                'amount': amount,
                'date': transaction_date,
                'time': transaction_time,
                'description': description
            })

        # Control Total for the individual account
        elif record_type == '49':
            _, total_amount, number_of_trans = line.split(',')
            account_data['total_amount'] = total_amount
            account_data['number_of_trans'] = number_of_trans

        # Control Totals
        elif record_type in ['98', '99']:
            _, total_amount, total_accounts = line.split(',')
            parsed_data['control_totals'][record_type] = {
                'total_amount': total_amount,
                'total_accounts': total_accounts
            }

    # Appending the last account_data if any
    if account_data:
        parsed_data['accounts'].append(account_data)

    return parsed_data


def create_bai2_files(parsed_data):
    header_data = parsed_data['header']
    header = f"01,{header_data['company_name']},{header_data['bank_name']},{header_data['date']},{header_data['time']},3,100,,2/"

    for account in parsed_data['accounts']:
        account_name = account['account_name']
        currency = account['currency']
        account_header = f"02,{account_name},YourBank,{currency},1/"

        transactions = []
        for transaction in account['transactions']:
            transactions.append(
                f"16,{transaction['transaction_code']},{transaction['amount']},,T,{transaction['date']},{transaction['time']},,{transaction['description']}/")

        account_total = f"49,{account['total_amount']},{account['number_of_trans']}/"

        # Construct the BAI2 file for this account
        bai2_content = header + '\n' + account_header + '\n' + '\n'.join(transactions) + '\n' + account_total

        # Write to a file
        with open(f"{account_name}.bai2", 'w') as file:
            file.write(bai2_content)


# Test the functions with the BAI2 data
bai2_data = """
01,CompanyABC,YourBank,230814,1630,3,100,,2/
02,Customer1-Account,YourBank,USD,1/
16,100,1000.00,,T,230814,1630,,Description1/
49,1000.00,1/
02,Customer2-Account,YourBank,USD,1/
16,105,1500.00,,T,230814,1630,,Description2/
49,1500.00,1/
98,77000.00,50/
99,77000.00,50/
"""

parsed_result = parse_bai2(bai2_data)
create_bai2_files(parsed_result)
