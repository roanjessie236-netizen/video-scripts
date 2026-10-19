"""《明天属于谁》new images (FLUX.1-schnell). name -> prompt. Style suffix appended to every prompt."""
STYLE = (", cinematic documentary film still, anamorphic lens, volumetric light, subtle film grain, rich detail, "
         "realistic, no text, no watermark")
P = {
 '01_keynes1930': "London 1930, a quiet study at night, mahogany desk with a black typewriter, handwritten manuscript pages and a fountain pen, green banker's lamp, rain streaking the window, warm tungsten light, shallow depth of field",
 '02_robotarms': "a bright modern automated factory, long rows of orange robotic arms assembling cars with sparks, no humans, morning light through skylights",
 '03_datacenter': "a vast AI data center at night, endless aisles of glowing server racks fading into haze, blue and amber light, a single engineer silhouetted",
 '04_overtime': "a modern office tower at night seen through the glass, exhausted office workers still at their desks under fluorescent light, city lights behind, melancholic",
 '05_machinecity': "a colossal golden fully automated megacity of machines glowing at dusk, cranes and drones, in the foreground a tiny crowd of human silhouettes looking up at it, awe and unease",
 '06_campfire': "prehistoric hunter-gatherers sitting around a campfire at night on the African savanna, an elder telling a story with expressive hands, sparks rising, Milky Way overhead",
 '07_cave': "torch-lit cave wall covered with ochre paintings of bison, horses and hunters, red hand stencils, a prehistoric hand holding a burning torch",
 '08_wheat': "Neolithic farmers harvesting golden wheat with flint sickles at sunset, mud-brick village and first granaries in the distance, Fertile Crescent",
 '09_ziggurat': "ancient Mesopotamian city, a towering ziggurat, laborers carrying grain sacks into a temple granary while priests and nobles watch from a terrace, scribes with clay tablets, golden dusty haze",
 '10_quern': "a medieval peasant woman grinding grain with a stone hand quern inside a dim thatched hut, firelight, flour dust in a beam of light, a lord's stone manor visible through the open door",
 '11_steammill': "1840s steam-powered flour mill interior, a giant iron flywheel and leather belts, rows of millstones, workers in caps, steam and shafts of light, sepia tones",
 '12_steam': "a Victorian steam locomotive bursting out of thick white steam at dawn beside smoking factory chimneys, Industrial Revolution England",
 '13_textile': "1850s Manchester cotton mill interior, hundreds of power looms in rows, women and child workers, shafts of light through tall windows, cotton dust in the air",
 '14_owner': "19th century factory floor seen from a high iron balcony, workers toiling at machines far below, in the foreground the silhouette of a factory owner in a top hat and frock coat looking down, dramatic contrast",
 '15_aiengine': "a colossal artificial intelligence core shaped like a steam engine built from light and circuitry, pistons of light, standing in a dark cathedral-like industrial hall, blue and amber glow",
 '16_aigrid': "night aerial view of a huge city where veins of glowing blue light spread through every building like an electrical grid, flowing into factories, hospitals and schools",
 '17_emptyoffice': "an empty corporate office floor at dawn, rows of vacant desks, monitors still glowing, a single employee carrying a cardboard box toward the elevator, cold blue light",
 '18_switchboard': "1940s telephone exchange, long rows of women switchboard operators with headsets plugging cables into tall switchboards, black and white photograph look",
 '19_station': "rush hour in a gigantic modern train station, thousands of commuters crossing in motion blur, huge departure boards glowing, high vantage point",
 '20_scaffold': "a construction worker on high steel scaffolding at sunrise above a city, hard hat, dust and sweat, golden backlight",
 '21_humanoids': "rows of humanoid robots working in a vast logistics warehouse, lifting and sorting boxes, one small human supervisor among them, cool industrial light",
 '22_paradox': "a gigantic fully automated warehouse overflowing with glowing goods behind a tall steel fence, a crowd of unemployed people standing outside in the rain looking in, dusk",
 '23_luddites': "England 1812 at night, masked weavers with sledgehammers smashing an iron power loom inside a mill by torchlight, splinters and sparks flying",
 '24_haijin': "Ming dynasty Chinese harbor in morning fog, tall wooden junks chained at the docks, wooden palisades and soldiers with spears blocking the port, muted colors",
 '25_flood': "a mighty muddy river in full flood surging through a narrow mountain gorge, storm light, spray, aerial view",
 '26_dujiangyan': "aerial view of an ancient Chinese irrigation work splitting a mighty mountain river into calm channels that feed vast green fields and villages, golden hour, Dujiangyan",
 '27_threeroads': "aerial view at dawn of one road splitting into three roads that lead to three distant cities: on the left a dark fortress city under storm clouds, in the middle a grey ordinary city, on the right a luminous green garden city in sunlight",
 '28_cloudcastle': "a gleaming fortress city floating above the clouds, bristling with server towers and antennas, cold beams of light descending to an endless grey grid far below where tiny people work at screens, ominous",
 '29_cloudserfs': "an endless dim hall of people wearing headsets labeling data at identical glowing screens, rows to the horizon, giant cold logos glowing above them, dystopian",
 '30_queue': "rainy night city street, a long queue of people with umbrellas waiting at a glowing automated welfare kiosk, worn coats, melancholic",
 '31_assembly': "a sunlit town square in a future garden city, citizens of all ages gathered in a wide circle raising their hands to vote, solar roofs and trees, robots tending gardens in the background, warm hopeful light",
 '32_harvest': "future farmland at golden hour, autonomous robots harvesting crops while families share a long communal table of food in the field, children running, hopeful",
 '33_workshop': "a bright community workshop, an old man teaching a child to paint, a young woman playing cello, people building a wooden boat together, a robot carrying timber, warm afternoon light",
 '34_march1886': "Chicago 1886, a huge crowd of workers marching down a street of brick buildings with banners, factory chimneys behind, dramatic sky, sepia",
 '35_hands': "close-up of many hands of different ages and skin tones lifting a heavy wooden beam together on a building site, warm sunlight, dust",
 '36_bridge': "dawn, a crowd of people from all walks of life building a bridge together across a chasm toward a bright future city on the far side, epic and hopeful",
 '37_gardencity': "aerial golden-hour view of a harmonious future garden city, green terraces, solar arrays, rivers and open public squares full of people, realistic and hopeful",
}

# v2 prompts (second pass, generated with --suffix _b)
P2 = {
    '21_humanoids': 'a row of bipedal humanoid robots with human-like bodies, arms and heads, walking through a vast logistics warehouse carrying cardboard boxes, one human supervisor with a tablet watching them, cool industrial light',
    '27_threeroads': 'epic aerial view at dawn of a single straight road that forks into three separate roads across a wide valley, the left road leads to a dark walled fortress city under storm clouds, the middle road leads to a grey ordinary town in fog, the right road leads to a bright green garden city in golden sunlight, a clear three-way fork in the foreground',
    '23_luddites': 'England 1812 at night, weavers in rough coats and cloth caps with soot-blackened faces swinging heavy sledgehammers to smash an iron power loom inside a textile mill by torchlight, sparks and wooden splinters flying, dramatic chiaroscuro',
}
