
---

## Conseils de mixage

### La question de l'ordre

Nous avons évoqué dans l'introduction la question de l'ambisonie d'ordre plus élevé ainsi que celle de son ordre. Tâchons maintenant d'expliciter ce concept et comment choisir ce paramètre en fonction de ses besoins.

L'ambisonie constitue une forme d'échantillonnage. En audio, nous sommes généralement assez au fait de la question de l'échantillonnage lors du passage du domaine analogique au domaine numérique. Dans ce contexte, une plus grande résolution d'échantillonnage (ou fréquence d'échantillonnage) permet de représenter un spectre fréquentiel numérique plus important^[On rappel que pour une fréquence d'échantillonnage $F_e$, un système numérique peut correctement représenter des fréquences allant jusqu'à $\frac{F_e}{2}$]. Si maintenant nous considérons un phénomène spatial et non plus temporel, nous pouvons appliquer une logique analogue : façon à un nombre de position dans l'espace en pratique illimité, il convient de limiter ce nombre de positions par un échantillonnage de l'espace.

En générale, cet échantillonnage est représenté par les haut-parleurs. Alors les mêmes règles que pour la conversion analogique-numérique s'appliquent : plus le nombre de haut-parleurs est grands, et plus sa répartition dans l'espace est homonogène, au mieux l'espace acoustique sera correctement échantillonné. ^[En pratique, il convient d'appliquer aux représentations spatiales le même raisonnement que nous utilisons pour l'échantillonnage temporel. Tout comme nous limitons l'échantillonnage fréquentiel en conversion analogique-numérique en fonction de nos capacités auditives, nous devrions également adapter la résolution spatiale d'un échantillonnage de l'espace à nos capacités de localisation, qui ont aussi leurs propres limites physiologiques.]

L'ambisonie est une abstraction supplémentaire, dont l'idée repose sur la représentation d'un champ acoustique en un point où chaque source sonore serait idéalement placée sur la surface d'une sphère. Dès lors, l'ambisonie n'échantillonne pas des positions possibles dans l'espace mais plutôt les composantes d'une sphère, également appélées harmoniques sphériques. Cependant, la même logique s'applique, plus ces harmoniques sphériques sont nombreuses, plus notre champs sonore sera fidèlement capturé et réstitué.

L'ordre ambisonique définit très exactement la résolution de notre champs ambisonique. Un ordre plus élevé a, dès lors, une plus grande résolution spatiale. Pour un ordre $N$, on obtient $(N+1)^2$ harmoniques sphériques. Cela correspond aux nombres de canaux audio dans un flux ambisonique d'ordre $N$.^[Cette formule s'applique pour de l'ambisonique 3D. En 2D, la relation entre l'ordre ambisonique et le nombre d'harmoniques sphériques/de canaux devient $2N+1$.]

Il convient maintenant d'établir une relation entre la résolution ambisonique (donc la valeur de l'ordre) et la densité d'échantillonnage de notre espace (nombre de haut-parleurs) ainsi que la position de ces échantillons (positions des haut-parleurs dans l'espace):

+ Premièrement, comme l'ambisonie est l'échantillonnage d'un champs acoustique en un point, on attent à ce que l'ensemble de haut-parleurs prévu pour la réstitution sonore soit tous placés sur une sphère. ^[Lors d'un déploiement in-situ, on peut s'adapter à la géométrie d'un lieu en appliquant des retards et des atténuation sur les haut-parleurs trop proches et ainsi les replacer virtuellement sur une sphère idéale.]
+ Deuxièmement, on espère tout de même un échantionnage régulier de l'espace, même si nous avons évoqué ci-dessus que certains décodeurs permette de s'adapter à des arrangement de haut-parleurs irréguliers.
+ Troisièment, il est fortement recommandé de toujours avoir plus de canaux d'enceintes que de canaux ambisonique. Par exemple, si je souhaite réaliser un mixage pour un ensemble de 32 haut-parleurs, alors je ne dois pas dépasser un flux ambisonique d'ordre 4 (dont le nombre de canaux est $(4+1)^2 = 25$). On essaye donc d'avoir l'ordre ambisonique le plus élevé possible en respectant cette contrainte.

Mais alors, quid de l'agnosticité de l'ambisonique par rapport à notre arrangement de haut-parleurs ? Il est vrai que nous mettons ici en évidence une contrainte de nombre de haut-parleurs. Cependant nous avons deux façons de nous en extraire.

+ Premièrement, un flux ambisonique d'ordre $N$ peut être réduit à tous les ordre inférieurs. En effet, il suffit simplement d'ignorer les canaux audio transportant les informations relative aux ordres trop élevé pour notre cas d'usage. Ainsi, nous pouvons décoder de l'ambisonie d'ordre trois vers de la stéréo et troncant l'ambisonie à l'ordre un.
+ Deuxième, il existe des algorithmes permettant d'*upscaller* l'ambisonie vers des ordre supérieurs.

Proposont maintenant une approche raisonnable de l'ambisonique.

Il me semble que l'ambisonie d'ordre trois représente un bon équilibre entre résolution et flexibilité. Un flux ambisonique du troisième ordre contient seize canaux. Nous pouvons donc correctement restituer des arrangements de haut-parleurs constitués de moins de 25 haut-parleurs. Au délà, il sera préférable d'appliquer une algorithme d'*upscalling* afin d'étendre la résolution de notre mixage. 

### Structurer sa console

![Proposition de routage lors d'un mixage en ambisonie](ressources/console_ambi.drawio.svg)

Examinons d’abord comment structurer le routage d’une session dans le contexte d’un mixage ambisonique. Dans le cadre d’une prise de son reposant sur de la multi-microphonie^[Un même instrument capté par ensemble de microphones de telle façon à échantillonner sa caractéristique sonore. Cette dernière est reconstituée en phase de mixage, par ajustement des équilibres de volumes entre les microphones après leur alignement en phase.], la première question qui vient est donc : faut-il encoder en ambisonie chaque microphone ?

Généralement, il est préférable d’encoder les différents instruments plutôt que leurs différentes sources d'enregistrement. Cela permet de conserver un flux audio mono ou stéréo le plus loin possible dans notre chemin du signal, ayant pour conséquence de simplifier le routage de notre console, de garder une bonne flexibilité de traitement, et, enfin, de limiter la ressource en calcules. Une basse, par exemple, est généralement captée à l'aide de quelques microphones et une DI. Il est alors judicieux de sommer d’abord l’ensemble de ces signaux pour former un bus dédié, le plus souvent monophonique, à l’instrument de basse. On peut ensuite encoder cet instrument.

Pour les instruments enregistrés grâce à un couple stéréophonique et complétés par des appoints^[Deux logiques s'appliquent ici. Soit, on considère un ensemble d'instruments, soit un unique instrument, mais généralement assez grand. Dans les deux cas, le couple de prise de son constitue la source de prise de son principale et les appoints ne sont joués que comme des compléments.], on aura alors tendance à appliquer la même méthodologie : router l’ensemble des microphones dans un bus (ici stéréophonique) et encoder le signal stéréo en ambisonie.

Dans les rares cas où un instrument est enregistré à l’aide d’un microphone ambisonique et complété par des appoints, on pourrait alors, dans ce cas, encoder directement les appoints en ambisonie avant de former le bus instrument. Une prise de son ambisonique est souvent intéressante pour capturer l’acoustique du lieu. Dans ce cas, elle peut être considérée comme étant séparée du bus instrument.

Concernant l’ajout de traitement et d’effets, il est alors vivement conseillé de réaliser un maximum de traitement avant l’encodage ambisonique. En effet, traiter 16 canaux est forcément beaucoup plus coûteux que d’en traiter deux (on pourrait se laisser dire huit fois plus coûteux.). De plus les plug-ins multicanaux sont rares, mais nous réaborderons ce point plus loin.

Concrètement, on placera alors la majorité, voire l’intégralité des traitements avant l’encodeur ambisonique dans la chaîne d’effet de la piste. Du point de vue de l’optimisation des ressources, il semble que certaines heuristiques d’optimisation dans REAPER fonctionnent moins bien sur des pistes multicanales, même si les plugins eux-mêmes n’ont que deux canaux d’entrée/sortie. Pour résoudre ce problème, il convient alors de placer les effets préencodage dans un conteneur qui, lui, n’aura que deux canaux.

### Gestion des effets

#### Égalisation et traitement linéaires et invariants temporellement de bus ambisonique

<!-- TODO: Screenshot ReaEQ 16 channels -->

L’égalisation de bus ambisonique ne pose pas de problème particulier. Il convient simplement d’appliquer la même correction à l’ensemble des canaux. Il faudra alors un outil supportant au moins 16 canaux pour de l’ordre trois. Le même raisonnement s'applique pour tous les traitements linéaires et invariants temporellement.

#### Compression et traitement non linéaire de bus ambisonique

<!-- TODO: Gif avec ReaComp, Chowtape Model, Syrah -->

La question de la compression d’un bus ambisonique est moins simple. La difficulté principale est que la présence d’énergie dans un canal ambisonique n’implique pas une relation directe avec sa position dans l’espace. Dès lors, la compression différenciée des canaux est contre-indiquée pour éviter la dégradation de la spatialisation.

On trouve alors deux solutions. La première, et la plus simple sont de compresser l’ensemble des canaux du flux ambisonique en ne détectant l’enveloppe que sur le premier canal, dit W.

L’autre solution consiste à décoder le signal ambisonique sur un t-design adéquat à l’ordre, puis de compresser le signal décodé, et, enfin, de réencoder le signal compressé.

Certains compresseurs permettent aussi une compression par masquage spatial. On ne compresse ainsi que certaines zones de l’espace. Le compresseur de la suite IEM en est un bon exemple.

Pour les autres types de traitement non linéaire (saturation, limiteur, etc), on appliquera le même raisonnement que pour la compression.

#### Gestion du side-chain

<!-- TODO: Gif side-chain + schema -->

Le side-chain est une technique de compression permettant de compresser un signal à partir de l’enveloppe d’un autre signal. Le cas classique, popularisé par les musiques électroniques, est la compression de la basse par l’enveloppe du kick.

Or, nos pistes ayant maintenant 16 canaux, il semble alors compliqué de pouvoir alimenter le circuit de détection d’un compresseur mono ou stéréo à partir d’un tel signal. Heureusement, nous avons une solution très simple à ce problème.

Le premier canal de n’importe quel signal ambisonique, appelé généralement canal « W », correspond à une directivité omnidirectionnelle. En d’autres termes, ce canal représente le signal de notre instrument, indépendamment de la spatialisation que nous avons pu lui faire subir.

Pour réaliser une compression en side-chain, on pourra alors envoyer le canal W de notre piste de kick (donc le premier canal) dans le canal 17 de la piste de basse que l’on souhaite compresser.

#### La gestion des départs auxiliaires et des effets en parallèle

<!-- TODO: Schéma routing -->

Abordons maintenant la question des départs auxiliaires. Il convient de distinguer deux cas pratiques :

* Alimenter un effet mono ou stéréo, qui sera par la suite encodé en ambisonie, à partir d’un signal déjà encodé
* Alimenter un effet ambisonique à partir d’une piste ambisonique

Avant de rentrer dans le détail, nous allons devoir détailler une astuce de mixage, également applicable  en mixage stéréophonique.

Plutôt que de directement router une piste vers un effet, type réverbération, on pourrait alors utiliser une piste intermédiaire, nous permettant de ce fait d’accéder à du traitement par envois dans un effet. En pratique, on commence par router la piste d’instrument dans une nouvelle piste, puis on place cette dernière dans une piste dossier. Sur ce dossier est instanciée la réverbération que l’on souhaite utiliser. Précisons par ailleurs qu’une piste ne consomme presque aucune ressource dans REAPER et que de telles manipulations de routage peuvent être largement simplifiées et automatisées par l’usage de scripts.

Revenons au cas d’un mixage ambisonique.

Dans le premier cas, nous allons appliquer l’astuce déjà abordée précédemment. On route le canal W de notre flux ambisonique vers une nouvelle piste. Cette piste est alors placée dans un dossier qui contient l’effet mono ou stéréo. On encode ensuite cet effet en ambisonie.

Dans le second cas, nous allons alors envoyer les 16 canaux ambisoniques vers la nouvelle piste qui sera elle aussi placée dans un dossier qui contient l’effet. Dès lors, comme nous avons une piste intermédiaire, nous pouvons utiliser un effet ambisonique pour tourner la scène ambisonique de notre instrument, seulement pour l’entrée de l’effet. On peut alors imaginer avoir un instrument venant de la gauche et avoir sa réverbération provenant de la droite.

#### Réverbération et synthèse d'espace

Un outil clé en mixage est la réverbération afin de créer une impression de profondeur dans l'image sonore. Dans le cadre d'un mixage ambisonique, le plus simple est alors d'utiliser des réverbérations ambisoniques. Le problème est que celles-ci sont rares ! On pensera notamment à :

+ L'IRCAM Verb de FLUX::
+ L'AmbiVerb de NoiseMaker
+ La FDN Reverb de IEM

Face à ce nombre limité d'outils, on est alors tenté d'exploiter des effets multicanaux, mais pas forcément ambisoniques.

##### Intégrer une réverbération multicanal dans un mixage ambisonique

On trouve aujourd'hui un grand nombre de réverbérations multicanales, principalement dédiées au Dolby Atmos. Celles-ci supportent en général douze canaux d'entrées (7.1.4), voire seize (9.1.6). Il conviendra de toujours décoder le signal audio ambisonique avant d'attaque une réverbération multicanal. On réencode ensuite le signal de la réverbération.

Si la réverbération employée propose un nombre de canaux suffisant et d'organisation spatial arbitraire, on préfèrera décodé le signal ambisonique vers des arrangements homogènes et uniformes (t-design par exemple).

##### Transformer une réverbération stéréo en réverbération ambisonique

Les réverbérations ambisoniques sont rares. Voici alors une petite astuce permettant de recycler des réverbérations stéréo. Bien sûr, il ne s’agit pas ici de réalisme acoustique, mais simplement de retrouver une sensation d’enveloppement. Voici l’ensemble de la chaîne de traitement de la piste de réverbération :

* On commence par tronquer l’ordre ambisonique pour obtenir un signal du premier ordre.
* On décode ce signal ambisonique sur un arrangement t-design 4
* On place une instance de réverbération sur les canaux 1-2 et une autre sur les canaux 3-4
* On applique un algorithme de décorrélation sur les canaux 3-4 (ou 1-2, peu importe).
* On réencode le t-design 4 en ambisonie du premier ordre
* On up-mix l’ambisonie d’ordre 1 vers l’ordre 3.

Expliquons un peu plus en détail.

Tout d’abord, le choix du premier ordre est vivement conseillé pour simplifier le réglage des réverbérations. En effet, il faudra régler deux instances, et pas une ! Mieux vaut alors ne pas multiplier le nombre d’instances pour que le travail ne devienne pas trop fastidieux.

L’arrangement t-design 4 contient quatre haut-parleurs, placés de façon homogène et uniforme. Il s’agit donc d’un cas idéal pour l’ambisonie.

L’étape de décorrélation est nécessaire pour garantir une différence suffisante entre les canaux pour que l’on n’ait pas l’impression d’entendre deux fois la même réverbération, et donc perdre totalement la sensation d’espace.

Après le réencodage, une étape d’up-mixing permet de rejoindre notre ordre ambisonique initial.

<!-- TODO: Lien vers tuto FX Chain -->
Ce travail étant laborieux, on s’empressera de créer une « FX chain » dans REAPER pour ne pas avoir à répéter ce processus.

#### Quels effets pour le traitement de signaux ambisoniques

Globalement, peu de constructeurs offrent leurs plug-ins en version multicanal. Particulièrement, l’ambisonie reste un marché de niche. Voici une liste non exhaustive de constructeurs particulièrement tournés vers cette technologie :

+ IEM (open source & gratuit)
+ SPARTA (open source & gratuit)
+ FLUX::
+ Sound Particule
+ Noise Maker
+ Blue Ripple (principalement payant, onéreux et sans version de démo !)
+ Audio Brewers (payant et sans version de démo !)

Certains constructeurs prennent le parti de supporter un grand nombre de canaux, sans particulièrement se préoccuper de leur usage :

+ REAPER (les principaux plug-ins supportent jusqu’à 128 canaux)
+ Melda Production (64 canaux)

Bien que d’apparence disgracieuse, les plug-ins natifs de REAPER sont d’excellentes qualités. L’ensemble des fonctionnalités est généralement exhaustif sans être trop compliqué, et la qualité sonore est remarquable. Dans le cas du compresseur, il est possible de compresser l’ensemble des canaux en ne détectant l’enveloppe que sur le premier canal. Cette méthode est très utile en ambisonie.

Les plugins de Melda Production peuvent également être une solution intéressante. Ils sont, cependant, souvent trop chargés en fonctionnalités de second ou troisième plan, et passent parfois à côté de choses élémentaires. L’UI est fastidieuse à naviguer et certains algorithmes sont franchement décevants (MAutoAlign). Mais pour autant, ils offrent un large panel d’outils dont la plupart s’adaptent bien au travail ambisonique, jusqu’au septième ordre. Particulièrement, leur MTurboReverb est une réussite !

Aussi important à mentionner, Jatin Chowdurry développe une excellente simulation à bande nommée ChowTapeModel et qui supporte un nombre arbitraire de canaux ! À tester urgemment.

Enfin, la plupart des constructeurs offrant du multicanal le font dans le contexte de l’écosystème Dolby Atmos. Aujourd’hui, il n’est pas si rare de trouver des plug-ins gérant du 9.1.6, donc potentiellement les 16 canaux d’un ambisonie du troisième ordre (Pro Q 4 de Fabfilter, par exemple). Pour les plug-ins plafonnant à du 7.1.4, on pourra toujours passer par une étape de décodage et de réencodage ambisonique. Cette approche est parfaitement justifiable pour des effets, comme les délais et la réverbération. Pour un traitement sériel, la dégradation de l’image spatiale risque de ne pas en valoir la chandelle.

### Le monitoring

À ce stage, nous ne sommes pas en mesure d'écouter notre mix. Pourquoi ? Un mixage ambisonique doit être décodé vers un arrangement de haut-parleur particulier afin de pouvoir être écouté. Entendons-nous, la question du décodage ambisonique est délicate et mériterais un article à part entière pour commencer à gratter la surface du sujet. Ici, nous nous contenterons de quelques recommandations.

#### Ambisonie vers stéréophonie

L'idée peut sembler étrange, pourtant, la stéréophonie reste le format de production dominant en audio. Le but ici n'est pas de retranscrire la sensation de spatialisation sur une paire de haut-parleurs, mais simplement de proposer une réduction robuste et efficace. Pour cela, l'UHJ est une solution intéressante. En effet, ce format ambisonique est un rematriçage de l'ambisonie du premier ordre. On a donc toujours quatre canaux, mais les deux premiers sont écoutables comme une stéréo classique. Encore mieux, il est possible de décoder une quadriphonie à partir de ces deux premiers canaux. On retrouve ici le principe du matriçage quadriphonique 4-2-4. Dolby s’en est d'ailleurs fortement inspiré pour créer son encoder-décodeur "Dobly Stereo" ^[Oui, le système **L**eft-**C**enter-**R**ight-**S**urround de Dobly se nomme bel et bien Dolby Stereo. On imagine alors toutes les confusions qui en ont résulté.]

En pratique, un convertisseur UHJ est disponible pour REAPER, au format JSFX ^[Format d'effet similaire au VST3 ou AudioUnit, mais dont le code est écrit en EEL, langage développé par... Cockos !] [ici](https://www.brucewiggins.co.uk/?page_id=78). C'est utilitaire est développé gratuitement par Bruce Wiggins.

#### Ambisonie vers un arrangement quelconque

Plusieurs outils permettent de décoder vers un arrangement de haut-parleur quelconque, on pense à AllRAD Decoder de la suite IEM et à AmbiDEC de SPARTA. Bien que cette discussion dépasse le cadre de cet article, il faut mentionner que l’utilisation d’un décodage AllRAD ou EPAD est souvent préférable, et ce, particulièrement lorsqu’on décode son signal ambisonique vers un arrangement de haut-parleurs qui n’est pas homogène.

#### Ambisonie vers binaural

Le monitoring d’une scène ambisonique en binaural est une option particulièrement intéressante, puisque l’on peut, en théorie, s’extraire de la contrainte du système de haut-parleurs. La faiblesse du rendu binaural réside souvent dans une dégradation des timbres. Cela dit, l'ambiBIN de SPARTA est un décodeur particulièrement bluffant en ce sens. Une option à explorer donc.


## Conclusions

Bien que le Dolby Atmos soit souvent présenté comme une révolution dans le domaine de la spatialisation sonore, il présente plusieurs défauts notables qui remettent en question son adoption massive. Les limitations techniques, telles que la dépendance à des systèmes de diffusion spécifiques et hétérogènes, la variation de la perception de la largeur de la source, et l'absence de solutions satisfaisantes pour le traitement de groupes d'objets, sont autant de freins à son utilisation. De plus, la complexité accrue du mastering et la qualité discutable du rendu binaural ajoutent à ces préoccupations.

En revanche, l'ambisonie, une technologie plus ancienne, mais tout aussi prometteuse, offre des avantages similaires sans ces inconvénients. Grâce à des techniques de matriçage et à des décodeurs améliorés, l'ambisonie permet une flexibilité accrue et une meilleure interopérabilité des outils. Les suites de plug-ins comme IEM et SPARTA, qui sont distribuées gratuitement et open source, facilitent l’adoption de cette technologie.

Pour les ingénieurs du son souhaitant explorer la spatialisation sonore, l'ambisonie représente une alternative solide et éprouvée. En utilisant des logiciels comme REAPER, qui supportent un grand nombre de canaux, il est possible de réaliser des mixages ambisoniques de haute qualité tout en conservant les habitudes et techniques de mixage stéréophonique.

Ainsi, plutôt que de se laisser séduire par les promesses marketing du Dolby Atmos, il serait judicieux de se tourner vers l'ambisonie, une technologie qui a fait ses preuves et qui continue d'évoluer grâce aux contributions de la communauté scientifique et des passionnés du son.