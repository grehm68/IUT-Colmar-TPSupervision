
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-

    # IUT COLMAR bandwidth simulator for Net-SNMP pass_persist.
    # Exposes IF-MIB (ifTable) and IF-MIB::ifXTable for 48 x 1Gbps ports and
    # makes 64-bit octet counters grow at rates that draw 'IUT COLMAR' when
    # visualized as bar heights across ports.

import sys, time

NUM_PORTS = 48

rates_bps = [0, 257142857, 257142857, 900000000, 257142857, 257142857, 900000000, 128571428, 128571428, 128571428, 900000000, 128571428, 128571428, 900000000, 128571428, 128571428, 0, 900000000, 257142857, 257142857, 257142857, 257142857, 900000000, 257142857, 257142857, 257142857, 900000000, 900000000, 128571428, 128571428, 128571428, 128571428, 900000000, 128571428, 128571428, 128571428, 900000000, 900000000, 257142857, 257142857, 257142857, 900000000, 900000000, 257142857, 385714285, 385714285, 385714285, 0]

state = {
    'in': {'counters': [0]*NUM_PORTS, 'last': [time.time()]*NUM_PORTS},
    'out': {'counters': [0]*NUM_PORTS, 'last': [time.time()]*NUM_PORTS},
}

IF_MIB      = '.1.3.6.1.2.1.2'
IF_TABLE    = IF_MIB + '.2.2.1'
IF_NUMBER   = IF_MIB + '.1.0'
IFX_TABLE   = '.1.3.6.1.2.1.31.1.1.1'

oid_map = {}

oid_map[IF_NUMBER] = ('integer', lambda: 48)

for idx in range(1, NUM_PORTS+1):
    oid_map[f"{IF_TABLE}.1.{idx}"] = ('integer', lambda i=idx: i)
    oid_map[f"{IF_TABLE}.2.{idx}"] = ('string', lambda i=idx: f"GigabitEthernet0/{i}")
    oid_map[f"{IF_TABLE}.3.{idx}"] = ('integer', lambda: 6)
    oid_map[f"{IF_TABLE}.5.{idx}"] = ('integer', lambda: 1_000_000_000)
    oid_map[f"{IF_TABLE}.7.{idx}"] = ('integer', lambda: 1)
    oid_map[f"{IF_TABLE}.8.{idx}"] = ('integer', lambda: 1)
    oid_map[f"{IFX_TABLE}.1.{idx}"] = ('string',  lambda i=idx: f"Gi0/{i}")
    def in_octets(i=idx):
        now = time.time()
        last = state['in']['last'][i-1]
        rate = rates_bps[i-1] / 8.0
        inc = max(0.0, (now - last) * rate)
        state['in']['counters'][i-1] += int(inc)
        state['in']['last'][i-1] = now
        return state['in']['counters'][i-1]
    oid_map[f"{IFX_TABLE}.6.{idx}"] = ('counter64', in_octets)
    def out_octets(i=idx):
        now = time.time()
        last = state['out']['last'][i-1]
        rate = rates_bps[i-1] / 8.0
        inc = max(0.0, (now - last) * rate)
        state['out']['counters'][i-1] += int(inc)
        state['out']['last'][i-1] = now
        return state['out']['counters'][i-1]
    oid_map[f"{IFX_TABLE}.10.{idx}"] = ('counter64', out_octets)
    oid_map[f"{IFX_TABLE}.15.{idx}"] = ('integer', lambda: 1000)
    oid_map[f"{IFX_TABLE}.18.{idx}"] = ('string', lambda i=idx: f"IUT COLMAR SIM Gi0/{i}")

sorted_oids = sorted(oid_map.keys(), key=lambda s: [int(x) for x in s.strip('.').split('.')])

def write_response(oid, typ, val):
    if typ == 'string':
        sys.stdout.write(f"{oid}	string	{val}")
    elif typ == 'integer':
        sys.stdout.write(f"{oid}	integer	{int(val)}")
    elif typ == 'counter64':
        v = int(val) & ((1<<64)-1)
        sys.stdout.write(f"{oid}	counter64	{v}")
    else:
        sys.stdout.write("NONE")
    sys.stdout.flush()

def handle_get(oid):
    if oid in oid_map:
        typ, prov = oid_map[oid]
        write_response(oid, typ, prov())
    else:
        sys.stdout.write("NONE")
        sys.stdout.flush()

def handle_getnext(oid):
    def to_int_list(s):
        return [int(x) for x in s.strip('.').split('.')]
    req = to_int_list(oid)
    for candidate in sorted_oids:
        if to_int_list(candidate) > req:
            typ, prov = oid_map[candidate]
            write_response(candidate, typ, prov())
            return
    sys.stdout.write("NONE")
    sys.stdout.flush()

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        cmd = line.strip().lower()
        if cmd == 'ping':
            sys.stdout.write('pong')
            sys.stdout.flush()
        elif cmd in ('get', 'getnext'):
            oid = sys.stdin.readline().strip()
            if cmd == 'get':
                handle_get(oid)
            else:
                handle_getnext(oid)
        else:
            sys.stdout.write('NONE')
            sys.stdout.flush()

if __name__ == '__main__':
    main()
