# MAPF pomoci sat

## O implementaci 
ProblémŘešíme Multi-Agent Pathfinding (MAPF) – hledání cest pro více agentů z bodu A do bodu B tak, aby nedošlo ke koliiź pomocí SAT. SAT solver musí splnit tyto logické klauzule:
Pohyb: Pokud je agent na políčku $u$ v čase $t$, musí být v čase $t+1$ na sousedním políčku (nebo čekat). Žádné teleportování.
Konzistence: Agent se nesmí rozdojit (být na dvou místech zároveň).
Kolize: Dva agenti nesmí být ve stejném čase na stejném políčku.
Prohození: Agenti se nesmí křížit (prohodit si místa na hraně) ve stejném kroku.ProstředíPracujeme na čtvercové mřížce (grid) o velikosti $N \times N$. V tomto konkrétním zadání je mřížka uvažována jako volný prostor bez statických překážek (zdí), řešíme pouze vyhýbání se agentů navzájem.


ImplementaceJazyk: Python.Knihovna: python-sat (konkrétně solver Glucose3).Princip: Skript zkouší hledat řešení pro čas $T=1, T=2, \dots$, dokud nenajde plán, kde jsou splněny všechny podmínky.

## Ukázkový běh
```
Instance mapf3.txt
4

start
(0,0)
(0,3)
(3,3)
(3,0)

end
(3,3)
(3,0)
(0,0)
(0,3)
```

```
Agent 0: (0, 0) -> (3, 3)
Agent 1: (0, 3) -> (3, 0)
Agent 2: (3, 3) -> (0, 0)
Agent 3: (3, 0) -> (0, 3)

Solving for 4x4 grid...

Solution Found:
Time Horizon: 6
Time   | Agent 0    | Agent 1    | Agent 2    | Agent 3
------------------------------------------------------------
0      | (0, 0)     | (0, 3)     | (3, 3)     | (3, 0)
1      | (1, 0)     | (0, 2)     | (2, 3)     | (3, 1)
2      | (2, 0)     | (1, 2)     | (1, 3)     | (3, 2)
3      | (2, 1)     | (1, 1)     | (0, 3)     | (2, 2)
4      | (2, 2)     | (2, 1)     | (0, 2)     | (1, 2)
5      | (3, 2)     | (3, 1)     | (0, 1)     | (0, 2)
6      | (3, 3)     | (3, 0)     | (0, 0)     | (0, 3)
```