# systemd user units

The production schedule (ADR-014). These are the installed copies of the units
in `~/.config/systemd/user/`, committed so the schedule is reviewable and
reproducible rather than existing only on one machine.

Stage A.1 recorded the daily pass as "scheduled" when what existed was a
`nohup`'d shell loop that died with its parent — 1h37m of unattended collector
downtime on 2026-08-18 followed. A claim that something is scheduled now means
a unit file exists.

Install:

    cp ops/systemd/solattn-*.service ops/systemd/solattn-*.timer ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now solattn-watch.service solattn-collect.service solattn-daily.timer
    loginctl enable-linger "$USER"     # survive logout / start at boot

Verify:

    systemctl --user list-unit-files 'solattn*'
    systemctl --user list-timers 'solattn*'
    loginctl show-user "$USER" -p Linger

`solattn-daily.timer` sets `Persistent=true`, so a run missed while the machine
was off fires on next boot. That overlaps deliberately with the checkpoint
catch-up window: a missed outcome checkpoint cannot be recovered once the
vendor's trailing history window closes.
