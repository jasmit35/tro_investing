\out as_of_balances.txt
\pset title "Balances as of `date  +%Y-%m-%d`"
\pset footer off

select account_name, sum(amount) as balance    
from tro.invest_trans, tro.accounts
where transaction_date <= '2000-12-31'
    and tro.invest_trans.account_fk = tro.accounts.account_id
group by account_name
order by account_name   
;
\o

