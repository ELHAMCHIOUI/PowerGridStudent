
from Terrain import Terrain, Case

class StrategieReseau:
    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[int]]:
        return -1, {}, []

#class StrategieReseauManuelle(StrategieReseau):
#    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[int]]:
#        # TODO
#        return -1, {}, []

#class StrategieReseauAuto(StrategieReseau):
#    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[int]]:
 #     # TODO
#        return -1, {}, []



class StrategieReseauManuelle(StrategieReseau):
    def configurer(
        self, t: Terrain
    ) -> tuple[int, dict[int, tuple[int, int]], list[tuple[int, int]]]:
        """Configuration manuelle du réseau.

        On demande à l'utilisateur :
        - d'ajouter des noeuds (ligne, colonne)
        - d'ajouter des arcs entre ces noeuds

        Le noeud d'entrée est le noeud posé sur la case d'entrée du terrain.
        """
        print("Configuration manuelle du réseau :")
        print("(indices de lignes et colonnes à partir de 0)")

        noeuds: dict[int, tuple[int, int]] = {}
        arcs: list[tuple[int, int]] = []

        # Saisie des noeuds
        next_id = 0
        while True:
            rep = input("Ajouter un noeud ? (o/n) : ").strip().lower()
            if rep != "o":
                break
            try:
                lig = int(input("  ligne : "))
                col = int(input("  colonne : "))
            except ValueError:
                print("Coordonnées invalides, noeud ignoré.")
                continue
            noeuds[next_id] = (lig, col)
            print(f"  -> noeud {next_id} = ({lig}, {col})")
            next_id += 1

        # Saisie des arcs
        while True:
            rep = input("Ajouter un arc ? (o/n) : ").strip().lower()
            if rep != "o":
                break
            try:
                n1 = int(input("  noeud 1 : "))
                n2 = int(input("  noeud 2 : "))
            except ValueError:
                print("Identifiants invalides, arc ignoré.")
                continue
            if n1 in noeuds and n2 in noeuds and n1 != n2:
                a, b = sorted((n1, n2))
                if (a, b) not in arcs:
                    arcs.append((a, b))
                    print(f"  -> arc ({a}, {b}) ajouté")
                else:
                    print("  -> arc déjà présent, ignoré")
            else:
                print("  -> au moins un noeud inexistant, arc ignoré")

        # Détermination du noeud d'entrée
        entree_coords = t.get_entree()
        noeud_entree = -1
        for nid, coords in noeuds.items():
            if coords == entree_coords:
                noeud_entree = nid
                break

        return noeud_entree, noeuds, arcs



class StrategieReseauAuto(StrategieReseau):
    """Stratégie automatique simple :
    - Pour chaque client, on crée un chemin rectiligne (Manhattan)
      depuis l’entrée, en évitant les obstacles avec un petit contournement.
    """

    def configurer(self, t: Terrain):

        entree = t.get_entree()
        clients = t.get_clients()
        hauteur = t.hauteur
        largeur = t.largeur

        cases_reseau = set()
        cases_reseau.add(entree)

        # ------------------------------------------------------
        # Fonction utilitaire : test si une case est libre
        # ------------------------------------------------------
        def libre(i, j):
            if not (0 <= i < hauteur and 0 <= j < largeur):
                return False
            return t.cases[i][j] != Case.OBSTACLE

        # ------------------------------------------------------
        # Fonction : créer un chemin simple entre deux points
        # ------------------------------------------------------
        def chemin_simple(src, dst):
            (si, sj) = src
            (di, dj) = dst
            chemin = []

            i, j = si, sj

            # -- Étape 1 : mouvement vertical vers di --
            while i != di:
                step = 1 if di > i else -1
                ni, nj = i + step, j

                if libre(ni, nj):
                    i = ni
                else:
                    # Contournement : essayer j+1 puis j-1
                    if libre(i, j + 1):
                        j = j + 1
                        chemin.append((i, j))
                    elif libre(i, j - 1):
                        j = j - 1
                        chemin.append((i, j))
                    else:
                        # Aucun contournement possible : chemin impossible
                        return []

                chemin.append((i, j))

            # -- Étape 2 : mouvement horizontal vers dj --
            while j != dj:
                step = 1 if dj > j else -1
                ni, nj = i, j + step

                if libre(ni, nj):
                    j = nj
                else:
                    # Contournement vertical
                    if libre(i + 1, j):
                        i = i + 1
                        chemin.append((i, j))
                    elif libre(i - 1, j):
                        i = i - 1
                        chemin.append((i, j))
                    else:
                        return []

                chemin.append((i, j))

            return chemin

        # ------------------------------------------------------
        # Construire les chemins pour tous les clients
        # ------------------------------------------------------
        for client in clients:
            c = chemin_simple(entree, client)
            for pos in c:
                cases_reseau.add(pos)

        # ------------------------------------------------------
        # Construction des noeuds
        # ------------------------------------------------------
        noeuds = {}
        id_par_case = {}
        for pos in sorted(cases_reseau):
            nid = len(noeuds)
            noeuds[nid] = pos
            id_par_case[pos] = nid

        # noeud d’entrée
        noeud_entree = id_par_case.get(entree, -1)

        # ------------------------------------------------------
        # Construction des arcs entre voisins
        # ------------------------------------------------------
        arcs = []
        for (i, j), nid in id_par_case.items():
            for ni, nj in [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]:
                if (ni, nj) in id_par_case:
                    a, b = sorted((nid, id_par_case[(ni, nj)]))
                    if a != b and (a, b) not in arcs:
                        arcs.append((a, b))

        return noeud_entree, noeuds, arcs
