\o ../reports/as_of_balances.txt
\pset title 'Balances as of `date+%Y-%m-%d`'
\pset footer off

select account_name, security_name, sum(amount) as balance    
from tro.invest_trans t, tro.securities s, tro.accounts a
where transaction_date <= '2000-12-31'
    and t.account_fk = a.account_id
    and t.security_fk = s.security_id
group by account_name, security_name
order by account_name, security_name 
;

\o

