Idea

Many companies have batch job scheduling systems that sends emails when a job fails.  Most of these emails 
end up sitting in an inbox with no accountability until someone get into the office and notices either the
failure or the email.

This new application, jPager, will provide an accountable escalation notification system.


User Stories

An individual contributor (IC) will be notified by email and text message when a job fails.  If the IC fails 
to reply within a specified tolerance time period (for example: 5 minutes for a critical job, 60 minutes for
a medium priority job and 180 minutes for a low priority job) the next person in the escalation chain is 
notified (for example, manager) and the IC is informed that the manager has been notified.

This sequence of events continues up the escalation chain (IC to manager to director to managing director to
CTO to president) until someone replies or the escalation chain is exhausted.


Planned Technology

1 - Front end: HTML / JavaScript / CSS / Bootstrap

2 - Back end: NoSQL (reference tables) & Block Chain (transactions)
