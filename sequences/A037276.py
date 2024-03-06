import logging
import sys

import gmpy2

from modules import factor
from sequence import Sequence


class A037276(Sequence):

    def __init__(self):
        super().__init__(lookup_dict={
            49: 77,
            77: 711,
            711: 3379,
            3379: 31109,
            31109: 132393,
            132393: 344131,
            344131: 1731653,
            1731653: 71143523,
            71143523: 11115771019,
            11115771019: 31135742029,
            31135742029: 717261644891,
            717261644891: 11193431873899,
            11193431873899: 116134799345907,
            116134799345907: 3204751189066719,
            3204751189066719: 31068250396355573,
            31068250396355573: 62161149980213343,
            62161149980213343: 336906794442245927,
            336906794442245927: 734615161567701999,
            734615161567701999: 31318836286194043641,
            31318836286194043641: 333431436916146111627309,
            333431436916146111627309: 33205716184556772142207827,
            33205716184556772142207827: 31367222155734752971376323127,
            31367222155734752971376323127: 733915126325777821480557336017,
            733915126325777821480557336017: 476734743112036198712947236602187,
            476734743112036198712947236602187: 377171280957470909577133234490256751,
            377171280957470909577133234490256751: 3096049809383121823389214993262890297,
            3096049809383121823389214993262890297: 73796236325118712936424989555929478399,
            73796236325118712936424989555929478399: 13118114526141133089538087518197265265053,
            13118114526141133089538087518197265265053: 319521441731977174163487542111577539726749,
            319521441731977174163487542111577539726749: 595415617656474189392601483764603009147911,
            595415617656474189392601483764603009147911: 13842314669573706744784027901056001426046777,
            13842314669573706744784027901056001426046777: 3129192501509379967095393172011476342474406759,
            3129192501509379967095393172011476342474406759: 3203927133121399320591151296378525102203388346189,
            3203927133121399320591151296378525102203388346189: 133119651853912195249113288820301002347322382772769,
            133119651853912195249113288820301002347322382772769: 11103725795898241052711667094407302642807490159301277,
            11103725795898241052711667094407302642807490159301277: 1152194718705941109372661574127837007959097317735411121,
            1152194718705941109372661574127837007959097317735411121: 6318653972357749718234812726673333988788742328093848793,
            6318653972357749718234812726673333988788742328093848793: 711111311391974493533533521186754240313734089696843349346661,
            711111311391974493533533521186754240313734089696843349346661: 3771113711016948131790459407678947892694155341923379077407684653,
            3771113711016948131790459407678947892694155341923379077407684653: 7310113562312583178332057129971031882457634609852680847686251943317,
            7310113562312583178332057129971031882457634609852680847686251943317: 3111197172271564982895268105721087453190074064393495190773755017652247,
            3111197172271564982895268105721087453190074064393495190773755017652247: 373111539295698434141591345095168649790005875768086611455076505611166279,
            373111539295698434141591345095168649790005875768086611455076505611166279: 33333711151101316117103176926136887884135060403955118931001222053567659972075047,
            33333711151101316117103176926136887884135060403955118931001222053567659972075047: 37987951744462008749649348751784002342702203325604103216176784227054268232116293,
            37987951744462008749649348751784002342702203325604103216176784227054268232116293: 711131272236782094454737267090807771975783627239622801952043181949336676523721088629,
            711131272236782094454737267090807771975783627239622801952043181949336676523721088629: 11875268711137089799261311878547509623397801472835395151221348397140205614034351359377,
            11875268711137089799261311878547509623397801472835395151221348397140205614034351359377: 727431892383195200824551792309011586997602061240784213075478539371666587718903373678159,
            727431892383195200824551792309011586997602061240784213075478539371666587718903373678159: 717133578549596081307550033105521651212411487965543982552577200370139716504126134573487841,
            717133578549596081307550033105521651212411487965543982552577200370139716504126134573487841: 1013140899118131107973159425637372267366503456262916700717404858255585899140058606434748914537,
            1013140899118131107973159425637372267366503456262916700717404858255585899140058606434748914537: 72234097425722814870501750027158400247194032517114645379347463054616952506288341051992127524371,
            72234097425722814870501750027158400247194032517114645379347463054616952506288341051992127524371: 13194364771297636926449071474339241979213097094329426579438949847711959739988164520170173919543019,
            13194364771297636926449071474339241979213097094329426579438949847711959739988164520170173919543019: 7313477112327919644117373641599001219748294379551351547309579716601707756498905354854859516129556133,
            7313477112327919644117373641599001219748294379551351547309579716601707756498905354854859516129556133: 7711631753166696505943917711251563303775439749470615275651919009839779126156077932235038449963463079517,
            7711631753166696505943917711251563303775439749470615275651919009839779126156077932235038449963463079517: 3337167244325056337062272469154317119778326007522724375712551901020784140917502333620946432057740074247159,
            3337167244325056337062272469154317119778326007522724375712551901020784140917502333620946432057740074247159: 95261436871495662012485084755467231617796842248675690632434479247655080197916188170687651874396287605885943,
            95261436871495662012485084755467231617796842248675690632434479247655080197916188170687651874396287605885943: 3732103413798200515523614556129221083508436120679893341907378249919955987757483932846633610599367336113869677,
            3732103413798200515523614556129221083508436120679893341907378249919955987757483932846633610599367336113869677: 2319871433879037214352668020240859650879911309004912859377573130578018169806150833129469702241285634418469092261,
            2319871433879037214352668020240859650879911309004912859377573130578018169806150833129469702241285634418469092261: 39670596449961538913327033806488198658171247720125704653139983198704160856892726169859475666929224642658253490099,
            39670596449961538913327033806488198658171247720125704653139983198704160856892726169859475666929224642658253490099: 1319160609702226564934871769367637604043150490881457998804263724628334834659339646664655301520918741800172705479717,
            1319160609702226564934871769367637604043150490881457998804263724628334834659339646664655301520918741800172705479717: 1578402296877084245636527845664762022955688856629818203814039896335212323787639106029711180264464450584714475831081,
            1578402296877084245636527845664762022955688856629818203814039896335212323787639106029711180264464450584714475831081: 1281681011724776539912245544578681765332794124035517737631220639339061394154385983823220581485388414661593519979370771,
            1281681011724776539912245544578681765332794124035517737631220639339061394154385983823220581485388414661593519979370771: 37493969578062893875484712355503626172786037279469976176282283397864072628868373427595840785303013447717379263356481433,
            37493969578062893875484712355503626172786037279469976176282283397864072628868373427595840785303013447717379263356481433: 7105964373243508243931003675985211574414672863780369000655971109926981296274442288093165186933753059824843132778546864729,
            7105964373243508243931003675985211574414672863780369000655971109926981296274442288093165186933753059824843132778546864729: 24122832398599675415341798874322269550625042517833527878130445640085060252589094308546324740821837930438456004090264769151,
            24122832398599675415341798874322269550625042517833527878130445640085060252589094308546324740821837930438456004090264769151: 11896511103812371181815335792688085739109227133107182349285614078812653263891607034642347735526263222971482322832583856613441,
            11896511103812371181815335792688085739109227133107182349285614078812653263891607034642347735526263222971482322832583856613441: 31913135441113536562986351721217907189480492770041397975778744916436090908111415209216521065245015362538780184733923955090125011,
            31913135441113536562986351721217907189480492770041397975778744916436090908111415209216521065245015362538780184733923955090125011: 23932175741061307650869938768491187430361231691730823694080908829571088699692224658011938594415822497545769437225933713909741322549,
            23932175741061307650869938768491187430361231691730823694080908829571088699692224658011938594415822497545769437225933713909741322549: 39116119196047318155881071321597670976075264953130076917334206317777952208821194636834060838300796681794309836215092286809999933859,
            39116119196047318155881071321597670976075264953130076917334206317777952208821194636834060838300796681794309836215092286809999933859: 313853327487748935034436140092523811338219703752124051891504042381774719137598761092693894443884014138933899804173004823156541697713,
            313853327487748935034436140092523811338219703752124051891504042381774719137598761092693894443884014138933899804173004823156541697713: 3935727133357825619154905876396719334634570794597874282359270708598778922377643006273044425599731834360178326725701290113727046644961,
            3935727133357825619154905876396719334634570794597874282359270708598778922377643006273044425599731834360178326725701290113727046644961: 175910857352311181508765228883191665525859591360314594929121853972071911623622370200394561800507172511384828996177438754510263275872371913,
            175910857352311181508765228883191665525859591360314594929121853972071911623622370200394561800507172511384828996177438754510263275872371913: 6163417420095268155477772364724250614226571232560116019241948254195923713574444418269087218170388702566637060708432758564543801513313435003,
            6163417420095268155477772364724250614226571232560116019241948254195923713574444418269087218170388702566637060708432758564543801513313435003: 330617927347719362558016823081075016119393892390194218645736560211718067925517775155309393407847029027375197651980758092755512331680882731929,
            330617927347719362558016823081075016119393892390194218645736560211718067925517775155309393407847029027375197651980758092755512331680882731929: 2920138047969149056299477827831764974474330563006732975755149892502017761442206397381501294987050078840501836673559420025718611870754546792073,
            2920138047969149056299477827831764974474330563006732975755149892502017761442206397381501294987050078840501836673559420025718611870754546792073: 73300743312988213606365618131350997307019427933601730313435852553855574587320243165126450409979970503810321948072508820320776101506693631743787,
            73300743312988213606365618131350997307019427933601730313435852553855574587320243165126450409979970503810321948072508820320776101506693631743787: 3333171418896363438153736871090049414067493978550880421960910045725733457082622904976800065728761972806264115655795567291460808947772426698634661509,
            3333171418896363438153736871090049414067493978550880421960910045725733457082622904976800065728761972806264115655795567291460808947772426698634661509: 5311350311588413526549742842157154523727074564821365993301638001206958026410300450845667511953219872049205059398636855089534014521039395489209448269731,
            5311350311588413526549742842157154523727074564821365993301638001206958026410300450845667511953219872049205059398636855089534014521039395489209448269731: 7111891315364123738139268537590206883527079655170564630066989225472455317256070999323579605002060949400881236203810641821862903434018510186009610511699191,
            7111891315364123738139268537590206883527079655170564630066989225472455317256070999323579605002060949400881236203810641821862903434018510186009610511699191: 677959934254009914833980611942772532349728015299596797125348335536627185801694933317807298312560463320551394686643698469578957649460916482413383929168101631,
            677959934254009914833980611942772532349728015299596797125348335536627185801694933317807298312560463320551394686643698469578957649460916482413383929168101631: 22787873745228235192246901332188811512526027533888306924151251209726148885575712332465133344456987746930138631822411149806794710441073001296631385753707501227,
            22787873745228235192246901332188811512526027533888306924151251209726148885575712332465133344456987746930138631822411149806794710441073001296631385753707501227: 7171475911948885760720914485834411805168216213202595468962232963739071441133541865184678001629601182607226312880348900246844848900227068283166325369629573991313,
            7171475911948885760720914485834411805168216213202595468962232963739071441133541865184678001629601182607226312880348900246844848900227068283166325369629573991313: 356967789830191754612671866731221000473935914416426723035020277235684120741250395611846772946133494685165561827338796028717898771987572324741651023755870645553949,
            356967789830191754612671866731221000473935914416426723035020277235684120741250395611846772946133494685165561827338796028717898771987572324741651023755870645553949: 13431828796555931252205350667723657189957893612838517267061540935917814791413258389142533635763834905022317403438538106689190395089953894891189281091736983632645331931,
            13431828796555931252205350667723657189957893612838517267061540935917814791413258389142533635763834905022317403438538106689190395089953894891189281091736983632645331931: 81477382431617858607629654669086224895030590860856949164853464798393151511356156289762200575122773801949600629560294634580313680599127053982894889995189794735466895119,
            81477382431617858607629654669086224895030590860856949164853464798393151511356156289762200575122773801949600629560294634580313680599127053982894889995189794735466895119: 723109393299415766611709588259118255231186151731975024460027282682597240263635669237085660011491232056156715909184026132747632727779809352896881830754843064666748922417153,
            723109393299415766611709588259118255231186151731975024460027282682597240263635669237085660011491232056156715909184026132747632727779809352896881830754843064666748922417153: 711152423533870512979274224151957712372340646615997384153962790982702619529979513297872090944082176810466905146436569031922355314552189529971609287404512991501436510263046431,
            711152423533870512979274224151957712372340646615997384153962790982702619529979513297872090944082176810466905146436569031922355314552189529971609287404512991501436510263046431: 7731391277221010738614940387293881196447153797210617319174266576457649040084823326638085447941270182143980995395782788476970814706644749940729528404612096239900219479360678030127,
            7731391277221010738614940387293881196447153797210617319174266576457649040084823326638085447941270182143980995395782788476970814706644749940729528404612096239900219479360678030127: 1789895092003836246073153208197850343216107335087443082143287923588860077733151721662275296467194175854379832571565911228616000410077677224181081033204896924979589411918456508547201,
            1789895092003836246073153208197850343216107335087443082143287923588860077733151721662275296467194175854379832571565911228616000410077677224181081033204896924979589411918456508547201: 3769474899201911338881950956011726678255032132484767164521661790375056741861961568511982561766109629656634221234431298994754209604778476433330905036092651869706813369438025592069129,
            3769474899201911338881950956011726678255032132484767164521661790375056741861961568511982561766109629656634221234431298994754209604778476433330905036092651869706813369438025592069129: 717196152260221223007872743384258441159930329660761921215561751901380895624107463991090737914695431991081178555838906948006630214230434758907150001616425065499127576368383425223083297,
            717196152260221223007872743384258441159930329660761921215561751901380895624107463991090737914695431991081178555838906948006630214230434758907150001616425065499127576368383425223083297: 1017881127626278375517915672586908038511152103070861311990567245289251993982856094156277577608404269873793786599973130102184325224471143204231199123108701419629477860118533938997808860701,
            1017881127626278375517915672586908038511152103070861311990567245289251993982856094156277577608404269873793786599973130102184325224471143204231199123108701419629477860118533938997808860701: 19314146316237012697733292207779163185166095579247748524094440604341643594119011333379159166944790863542342035580567700871333581386748195916535938401239061672133983522915259717378301248272957,
            19314146316237012697733292207779163185166095579247748524094440604341643594119011333379159166944790863542342035580567700871333581386748195916535938401239061672133983522915259717378301248272957: 371889486882611516222054948027230527090755632007249470562618772705150226666757269379397851701811665148878558631224270351349942558007042949108773010056679050116253803574164282317671667506144553,
            371889486882611516222054948027230527090755632007249470562618772705150226666757269379397851701811665148878558631224270351349942558007042949108773010056679050116253803574164282317671667506144553: 59411178172397606585858071483968333641901768119533227243507346216421306978978076569660842348180928237269671741847251176442051230228132913831062450594358151265525588922400325147005752739661876019,
            59411178172397606585858071483968333641901768119533227243507346216421306978978076569660842348180928237269671741847251176442051230228132913831062450594358151265525588922400325147005752739661876019: 372614130011918111411072782128567282855315039253816031044750271908309890598118753652349724122362534188076740444817312238388545260672268685822022236441690231083090644547260008735024402747827401799039,
            372614130011918111411072782128567282855315039253816031044750271908309890598118753652349724122362534188076740444817312238388545260672268685822022236441690231083090644547260008735024402747827401799039: 179372999150111947465573371636227257234535197886125889520915411267935624560746503422154192060735654946200813373057159461202228335655539331091962808118604240541265521091783630320332376356814622960926093,
            179372999150111947465573371636227257234535197886125889520915411267935624560746503422154192060735654946200813373057159461202228335655539331091962808118604240541265521091783630320332376356814622960926093: 19569683745003986525258674057129718148782354799242131771052383785311834993979061208604132871538232335055323716004722254150586483843313158263592817803974805568194113667109128698119199668739510916110374031,
            19569683745003986525258674057129718148782354799242131771052383785311834993979061208604132871538232335055323716004722254150586483843313158263592817803974805568194113667109128698119199668739510916110374031: 3333171733131104769163366751448517289166567507647762862045807583832036089265238362727899898079339354405235894851158438173650422654045381281492110241570912663690359389778909529774668266908592416498348856300467,
            3333171733131104769163366751448517289166567507647762862045807583832036089265238362727899898079339354405235894851158438173650422654045381281492110241570912663690359389778909529774668266908592416498348856300467: 107228613700198301407581535317003127481633253493734999759793567866901093615000660202729464171721664981941672355364244979546033697842584415925459377122074668562830876181453746637033053422944132164520381030890363,
            107228613700198301407581535317003127481633253493734999759793567866901093615000660202729464171721664981941672355364244979546033697842584415925459377122074668562830876181453746637033053422944132164520381030890363: 33727891305536904984515142156267396306831071512921191821889578536857126530781642034476718502313327970096030290047554836547278094547793019053742289833736552786286890695511249799288531238767159656593259713779239907,
            33727891305536904984515142156267396306831071512921191821889578536857126530781642034476718502313327970096030290047554836547278094547793019053742289833736552786286890695511249799288531238767159656593259713779239907: 3317920935997085994354428625165832568216205357586289833142037175405671543840180497605235553518623409887008129131154591902443542692796119052153354278268053219461692294780071701582743195860483406058135687932783227337,
            3317920935997085994354428625165832568216205357586289833142037175405671543840180497605235553518623409887008129131154591902443542692796119052153354278268053219461692294780071701582743195860483406058135687932783227337: 371247369442311247884384744096581550455991236745443829514960155286777455104133138209996227094175301272382137857317340226024600046391016469549509423923218156186003630641092474661686802611798393277995398615210685360809,
            371247369442311247884384744096581550455991236745443829514960155286777455104133138209996227094175301272382137857317340226024600046391016469549509423923218156186003630641092474661686802611798393277995398615210685360809: 2986278934525780677744979651300824439892156209930544960268296532391479820611369205267924863199536513832217953233168124361466902944146099855900103168298336973117660251047536278410398151410570271601591803427840895029573,
            2986278934525780677744979651300824439892156209930544960268296532391479820611369205267924863199536513832217953233168124361466902944146099855900103168298336973117660251047536278410398151410570271601591803427840895029573: 23818343988967755319547774376150791059914483440372080567294617121633338433975799345243491320079067479932342810228530227200671373510511696126019808808236481554559919288831861639367780232986027143088905987751279464964569,
            23818343988967755319547774376150791059914483440372080567294617121633338433975799345243491320079067479932342810228530227200671373510511696126019808808236481554559919288831861639367780232986027143088905987751279464964569: 71179197499409115121643897860409539199657108743448881976777365182339100431511269691096985452914054473614467986092088944695904034402222685589020756827368721041445591222744297916341457480713464115193376230466835244912640871,
            71179197499409115121643897860409539199657108743448881976777365182339100431511269691096985452914054473614467986092088944695904034402222685589020756827368721041445591222744297916341457480713464115193376230466835244912640871: 4399148103071904527577341666934161882323332593346117341628454893904180591823269710304105839284831007210929690372297543197305275562746521785454576365391992704799651330917664301820569983349019836821297297023820367595810298059,
            4399148103071904527577341666934161882323332593346117341628454893904180591823269710304105839284831007210929690372297543197305275562746521785454576365391992704799651330917664301820569983349019836821297297023820367595810298059: 175339012050993072922824766566567768442402519373117953746842217881025776726209350227017766087740033329776997389899143770314061659434892385152175106155830668276820914577750582095477513289249502333328800859279231550379002369437,
            175339012050993072922824766566567768442402519373117953746842217881025776726209350227017766087740033329776997389899143770314061659434892385152175106155830668276820914577750582095477513289249502333328800859279231550379002369437: 3671737043344925236335073739083150181679161380508176090501426702672788176702435652976517619169402201438951236090204889092306488073470764482198728531631481172682230888933717510814904903322277031646678719107694729251345099067292373,
            3671737043344925236335073739083150181679161380508176090501426702672788176702435652976517619169402201438951236090204889092306488073470764482198728531631481172682230888933717510814904903322277031646678719107694729251345099067292373: 3134619919193102180045258151265458684699434871683669372558183911632014946908126268643562324034274510802291607219184297470819235539199930760931178111375471383218619065999437213692862228834144004507405010566482975467510026391893737893,
            3134619919193102180045258151265458684699434871683669372558183911632014946908126268643562324034274510802291607219184297470819235539199930760931178111375471383218619065999437213692862228834144004507405010566482975467510026391893737893: 37619236425787331056788951520890313861395378799980671913242639228855682038275386963913139191902992119830964965826611351449575007747715257875980823060025161989259479167407618986741511789127217197204189147347509304829105884519047315609357,
            37619236425787331056788951520890313861395378799980671913242639228855682038275386963913139191902992119830964965826611351449575007747715257875980823060025161989259479167407618986741511789127217197204189147347509304829105884519047315609357: 3731193016801185925703625922156723182924383293415517890939196687565977107005064913622292894971684071867003068986128212655141573741060418424816873907952381376587035978526994468873432733002148738098978790716880067275297057598545539637098807,
            3731193016801185925703625922156723182924383293415517890939196687565977107005064913622292894971684071867003068986128212655141573741060418424816873907952381376587035978526994468873432733002148738098978790716880067275297057598545539637098807: 1312721660787364148211209433269635873337345728710802324714959340216539677015411086133710572310258942683190562148481349981529646166666457710725946445425378874927493014424039752199250428288421137405176030220678259087985564776929828767588285591,
            1312721660787364148211209433269635873337345728710802324714959340216539677015411086133710572310258942683190562148481349981529646166666457710725946445425378874927493014424039752199250428288421137405176030220678259087985564776929828767588285591: 3132352184565093556986871176277247131998844752030055462128389161986882946018325701897447678459077350750421945197535866122763460428979379684365121200540074047591147140542460496235458138489508677738334605570121814426485117922308620342259219122429,
            3132352184565093556986871176277247131998844752030055462128389161986882946018325701897447678459077350750421945197535866122763460428979379684365121200540074047591147140542460496235458138489508677738334605570121814426485117922308620342259219122429: 199832663786079934389995249216560515850463645243950894581151544200396046009994265181289778058956266070332646701004865005957729411315846193521722462000233024701829247399958531604693185089159216840434539144347083910244676679456195607708735639313427,
            199832663786079934389995249216560515850463645243950894581151544200396046009994265181289778058956266070332646701004865005957729411315846193521722462000233024701829247399958531604693185089159216840434539144347083910244676679456195607708735639313427: 3333392572567849565913669342466131125299712089711795346540523800293191513822000800271461386480080346398595476622849042477355693361771517488657715528360851816690277903228983539095849848639342470604943315995243199368402520964016310098028081653466011863,
            3333392572567849565913669342466131125299712089711795346540523800293191513822000800271461386480080346398595476622849042477355693361771517488657715528360851816690277903228983539095849848639342470604943315995243199368402520964016310098028081653466011863: 227523862833985230370000334918470225660868578167713903969185918301822379597057446412821594399022506045260907988881750768134579956275599251807250458645782428383408927406009458945953444463564355939175881354250587345715900852529152005426789424094520021323,
            227523862833985230370000334918470225660868578167713903969185918301822379597057446412821594399022506045260907988881750768134579956275599251807250458645782428383408927406009458945953444463564355939175881354250587345715900852529152005426789424094520021323: 323995252331214375508128444340012696278287835799918502553958149309022902265905740704656192615777121823373615478946901038954613405576374699716537654195779115452085989138575434836851289636159339542929128160183686876788663786928798769682882741367314660621029,
            323995252331214375508128444340012696278287835799918502553958149309022902265905740704656192615777121823373615478946901038954613405576374699716537654195779115452085989138575434836851289636159339542929128160183686876788663786928798769682882741367314660621029: 31591559896269666666598271323929987368130648086914375205708609469455240795758009093092999931626631706893838237446804628957426949545161439643850763983152977771070456646529606514514350669236880120878528179383004060084979184123521819930400481691041161410407051,
        }, start_index=1)

    def calculate(self, n):
        return gmpy2.mpz("".join(map(str, sorted(factor.factorize(n)))))


sys.modules[__name__] = A037276()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A037276()
    # seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")

    # generate lookup dict for A037274
    print("{")
    val = 49
    for k in range(1, 119):
        newval = seq(val)
        print(f"{val}: {newval},")
        val = newval
    print("}")