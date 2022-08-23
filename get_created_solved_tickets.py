import pandas as pd
from snowflake_utils.analyticsdb_io import AnalyticsDBConnector
import re

db_io = AnalyticsDBConnector(schema_name='RPT_CS_DATA')
db_io.use_local_connection('volodymyr.panov@transferwise.com')
schema = 'RPT_CS_DATA'

start_period = input(f'specify start date in a yyyy-mm-dd format as a string:')
end_period = input(f'specify end date in a yyyy-mm-dd format as a string:')

while re.search(r'(\d+-\d+-\d+)', start_period) is None or re.search(r'(\d+-\d+-\d+)', end_period) is None:
    print('wrong format')
    start_period = input(f"specify start date in a 'yyyy-mm-dd' format:")
    end_period = input(f"specify start date in a 'yyyy-mm-dd' format:")

created_script = """
select count(CONTACT__CHANNEL) as created_count
from RPT_CS_DATA.ANALYTICAL_CSOPS_PERFORMANCE__ALL_CONTACTS_SUMMARY
where CONTACT__DIRECTION = 'inbound'
and CONTACT__IS_NO_REPLY_TICKET = 'false'
and CONTACT__CHANNEL = 'email'
and date_trunc(day, CONTACT__CREATED_AT_TS) between {} and {}
and CONTACT__IS_FOR_CS = 'true'
and CONTACT__FIRST_QUEUE_NAME ilike '%cs%'
""".format(start_period, end_period)
created = db_io.fetch(created_script, lower_case=True)

solved_script = created_script = """
select
    count(CONTACT__CHANNEL) as solved_count
    from RPT_CS_DATA.ANALYTICAL_CSOPS_PERFORMANCE__ALL_CONTACTS_SUMMARY
    where CONTACT__DIRECTION = 'inbound'
        and CONTACT__IS_NO_REPLY_TICKET = 'false'
        and CONTACT__CHANNEL = 'email'
        and date_trunc(day, contact__last_action_ended_at_ts) between {} and {}
        and CONTACT__IS_FOR_CS = 'true'
        and ZENDESK_TICKET__CURRENT_STATUS = 'solved'
        and contact__last_queue_detail ilike '%cs%'
""".format(start_period, end_period)

solved = db_io.fetch(solved_script, lower_case=True)


result = pd.concat([created, solved], axis=1, join="inner")

print(result)

exit()
