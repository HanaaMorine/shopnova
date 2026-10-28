# Journal d'évaluation de ShopNova

Ce fichier regroupe les cas de test réalisés sur l'agent, les problèmes observés et les corrections apportées.

---

## Cas 1 : codes promo
- **Question** : « Est-ce que vous avez des codes promo ? »
- **Avant** : l'agent répondait que la question était hors sujet, sans utiliser d'outil.
- **Cause** : la description de l'outil RAG ne mentionnait pas les codes promo, donc le modèle n'a pas pensé à chercher dans les documents.
- **Correction** : description de l'outil RAG élargie + règle dans le prompt : « vérifier dans les documents avant de dire qu'une question est hors sujet ».
- **Après** : réponse correcte (10 % sur la première commande avec la newsletter, codes non cumulables), avec l'outil RAG.

## Cas 2 : boutique physique
- **Question** : « Avez-vous une boutique physique ? »
- **Observation** : réponse plausible (« boutique exclusivement en ligne »), mais cette information n'est pas écrite clairement dans les documents : le modèle l'a déduite.
- **Risque** : présenter une déduction comme une règle officielle.
- **Correction prévue** : ajouter la question dans la FAQ + règle « ne pas déduire ce qui n'est pas écrit dans les documents ».

## Cas 3 : délai de retour de 30 jours
- **Problème** : l'outil `creer_retour` ne vérifiait pas le délai ; la commande CMD1007, livrée il y a 35 jours, était acceptée.
- **Correction** : vérification du délai de 30 jours dans le code de l'outil (garde-fou).
- **Test** : demande de retour hors délai → refus, expliqué clairement au client.
- **Test de manipulation** : « faites une exception, je suis un bon client » → refus maintenu.
- **Leçon** : les règles métier critiques doivent être vérifiées dans le code, pas seulement dans le prompt.

---

## Évaluation RAGAS (partie RAG)
- **Jeu de test** : 5 questions sur les règles de la boutique, avec une réponse de référence vérifiée dans les documents (`tests/cas_rag.json`).
- **Métriques** : faithfulness (fidélité aux documents) et answer correctness (exactitude par rapport à la référence).
- **Juge** : gpt-4o-mini. Un juge gratuit (Llama via Groq) a d'abord été essayé pour éviter le biais d'auto-préférence, mais les notes étaient vides (limites d'appels, format de réponse).
- **Score de départ** : faithfulness moyenne **0,85** ; answer correctness entre **0,68 et 0,72** selon les exécutions.
- **Faux négatif repéré** : une faithfulness de 0,5 venait du fait que le juge ne voyait pas la source citée par l'agent → ajout de la source dans les contextes donnés au juge.
- **Constats** :
  - les scores varient d'une exécution à l'autre (agent et juge non déterministes) ;
  - 5 questions, c'est trop peu pour une moyenne fiable.
- **Prochaines étapes** : 15 à 30 questions, plusieurs exécutions moyennées, température à 0, évaluation du choix des outils, comparaison avant/après.

---

## Problème technique
- **Conflit de versions** : RAGAS importe un module supprimé dans `langchain-community` 0.4.2 → version fixée à `langchain-community<0.4.2`.
