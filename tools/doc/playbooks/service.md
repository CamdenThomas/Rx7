# Playbook: log a service act

One row in `00-CAR`: the work, the mileage, the parts fitted, anything found wrong. No
project needed.

A `kind=drive` answer is one `drives` row: its id is the answer's target, `date` from its
`at`, `odometer` its choice, and `kind` is `set` for an `odo-` target and `drive` otherwise.
His words go into `from`, `to` and `note` as he wrote them. `rx7.py apply` writes these;
a reading lower than the one before it is a finding it leaves for you: raise it, and never
write it over. Delete the inbox row once the drives row exists.
