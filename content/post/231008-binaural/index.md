---
title: Synthèse binaural - limites des applications
author: Jean-Loup Pecquais
lang: fr 
date: "2023-10-08"
categories: 
  - spatialisation
  - binaural
format: hugo-md
jupyter: python3
---

## Préambule

Depuis quelques années, l'engouement pour le son immersif semble grandissant, en tout cas du côté des constructeurs. Sans doute, l'adoption du format ADM, parfum Dolby, pour la bibliothèque de contenu immersif chez Apple Music a touché un grand nombre d'utilisateurs, mais sans doute sans que ceux-ci en réellement conscience.

Pour les adeptes de l'écosystème Apple, la consommation de contenu audio via Apple Music se fait maintenant par défaut en immersif (lorsque le contenu existe, bien-sûr). L'implication direct est que ce public là écoute donc très probablement du binaural sans le savoir.

Alors revenons rapidement sur ce fameux "binaural". Cette technique de spatialisation cherche à reproduire, imiter l'écoute humaine, ou plus justement, à simuler l'organe de captation sonore que sont nos oreilles. Cela passe par deux moyens possibles :

-   Soit par un enregistrement, via des microphones miniatures placés dans les oreilles d'un preneur de son, soit par des têtes artificielles (type Neumann KU100) - On parle de **binaural natif**.
-   Ou alors par un traitement du signal permettant de reproduire l'influence de notre tête et de nos oreilles dans notre expérience d'écoute naturelle - On parle de **binaural de synthèse**.

Dans le cas de la plateforme Apple Music, nous sommes dans le second cas.

La synthèse binaural s'appuie sur deux traitement principaux :

-   L'application d'un retard sur le signal pour simuler l'espacement entre nos deux oreilles
-   L'application d'un filtrage cherchant à reproduire le détimbrage produit par notre corps (principalement le couplage entre oreille externe, tête et buste) sur une onde sonore. On utilise alors des **HRTF/HRIR** (Head Related Transfer Function/Head Related Impulse Response), l'un étant la représentation dans la domaine temporel (ou fréquentiel) de l'autre.

## Performance de la synthèse binaurale

L'argument numéro un présenté par les partisants de l'audio immersif, est le gain **qualitatif** innérant à une réstitution dite immersive. Il parait cependant curieux d'aborder un rendu binaural de contenu musical simplement sur un critère qualitatif. Que cela signifie-t-il ?

Si l'on creuse un peu plus l'argumentaire commercial, derrière la qualité se cache le confort d'écoute. Ecoute du binaural, au casque, serait plus confortable que de la stéréophonie simple. Là encore, l'idée de confort semble assez discutable car plusieurs critères peuvent être envisagés pour tenter de décrire le confort d'écoute, par exemple :

-   La restitution des timbres
-   La plage dynamique
-   La précision de localisation
-   La sensation d'immersion dans la scène sonore

En abordant cette liste de critères de façon rationnelle, la question de la plage dynamique entre un rendu binaural et un rendu stéréo semble peu déterminante <!-- TODO: POURQUOI? -->. Sur la question de la précision de localisation et d'immersion, c'est ici que le binaural représente un avantage. Une écoute stéréophonique au casque produit un certain nombre de distortion, principalement du à l'angle de 180° entre les deux enceintes d'un casque (contre 60° en stéréo) et à la perte des chemins croisés. <!-- Faire un schéma -->

Cependant, l'application de filtres HRTF est loin d'être indolore sur la restitution des timbres. Lorsque cette question est prédominante (et elle est critique dans la plupart des genres musicaux), la stéréophonie, même au casque, est souvent préférée.

Dès lors, l'ensemble "stéréo" et "binaural" semble être opposé, le premier privilégiant les timbres, le second la spatialisation, sans compromis apparant.

## Les limites de l'approche binaurale

<!-- Nous avons donc mis à jours une difficulté à préserver les timbres lors d'un rendu binaural.  -->

Le binaural n'est pas non plus exempt de défault de localisation. Le premier, assez connu, est la confusion avant/arrière. Ce phénomène s'explique assez simplement : nous entendons principalement à l'avant ce que nous voyons, et à l'arrière ce que nous ne voyons pas. Ecouter alors une musique mixée en binaural risque de produire un effet de repliement des sources à l'arrière de l'auditeur, simplement du au fait qu'il n'y a pas de contexte visuel. Sans mauvaise foi, on pourrait tout de même estimer que ce problème provient plus de notre perception que du binaural lui-même, mais il entâche tout de même l'expérience d'un public naïf.

L'autre défaut majeur du binaural est son approche "signal" de la spatialisation. En effet, l'idée originelle est de simuler l'écoute naturelle humaine. Or, le simulation du binaural s'arrête au tympan, et ne prend alors pas en compte tous les mécanismes cérébraux qui ont lieu lors de notre écoute. En d'autre terme, on pourrait dire que le binaural **entend** mais n'**écoute pas**. Comment cela se concrétise-t-il ?

Prenons un cas d'usage très simple du binaural : le monitoring. Vous êtes en déplacement, et vous souhaitez mixer un programme quelquonque, comme si vous êtiez dans votre régie. L'emploi du binaural (et d'un réverbération approprié) semble tout indiqué pour simuler la présence de haut-parleurs au casque. Bien souvent, lorsqu'on essaye ce type de stratégie, on rencontre rapidement un problème de **dégradation du centre fantôme**.

> **Tip**
>
> Pour rappel, le centre fantôme est un concept de psycho-acoustique stipulant que si un son est émis avec la même intensité sonore et la même phase de deux enceintes, alors le son semblera être émis d'un point médiant, entre les deux enceintes. Il est donc fantôme car il n'y a pas de transducteur physique à l'endroit où il est perçu. La stabilité de ce centre fanôme dépend largement de l'angle entre les enceintes. Il n'est généralement pas recommandé de dépasser les 60° de la stéréophonie.

Le problème rencontré est au final assez simple à décrire. Lorsque l'on "virtualise" une source stéréo en binaural, tout ce qui est normalement perçu comme central dans la scène sonore est émis en deux points de l'espace dans notre rendu binaural, dans l'enceinte gauche et dans l'enceinte droite. De par les algorithmes utilisés par la synthèse binaural, on créer alors un filtrage en peigne sur le centre fantôme, résultant en une dégradation encore plus forte du timbre.

Si l'apparition de ce filtre en peigne semble évident en binaural, il est alors surprenant de se rendre compte qu'il n'existe pas dans notre expérience d'écoute de la stéréophonie. Aucun mixeur, aucun auditeur ne s'est jamais plein d'un tel phénomène face à un système de diffusion stéréophonique. On mesure ici l'importance de tout ce qui se situe derrière le tympan dans notre expérience d'écoute. Nous devrions entendre un filtre en peigne, or, notre cerveau le compense. On peut alors assez solidement affirmer que le binaural ne tient pas compte de notre perception et simule seulement une partie de notre organe auditif.

## Que faire de ce bilan ?

Malgré l'axe un peu désabusé de cet article, il ne faut pas condamné le binaural. Il s'agit certainement de la solution la plus à même de faire découvrir le son immersif à une large nombre de personne. La bonne nouvelle, c'est que des solutions, ou des compromis, existent pour palier aux problèmes évoqués ci-dessus, et feront l'objet d'articles subséquents. En deux mots, certaines approches du binaural font le choix d'abandonner les HRTF pour des approches dîtes paramétriques. Il est également possible d'améliorer les problèmes de centre fantôme, en extrayant ce dernier des sources stéréophoniques.

Là ou le bas blesse, c'est bien pour nos plateforme de streaming. Si celle-ci font le choix du mixage orienté objet comme format de diffusion, alors elles seules peuvent faire les modifications nécessaires à l'amélioration du rendu binaural. Le mixeur **n'a pas la main**. Nous aurons sans doute l'occasion de rediscuter ici du mixage orienté objet, et particulièrement du Dolby Atmos, mais peut être cette article vous mettra déjà en tête l'idée que tout ceci n'est peut être pas très bien fini.
