"""Случайные сценарии преступлений для системы преступлений."""

import random
import discord
from redbot.core import bank, commands, Config
from typing import Union, List, Dict, Optional

# Константы для уровней риска и коэффициентов успеха
RISK_LOW = "низкий"
RISK_MEDIUM = "средний"
RISK_HIGH = "высокий"

SUCCESS_RATE_HIGH = 0.75
SUCCESS_RATE_MEDIUM = 0.50
SUCCESS_RATE_LOW = 0.30

async def format_text(text: str, ctx: Union[commands.Context, discord.Interaction], **kwargs) -> str:
    """Форматирование текста путем замены заполнителей фактическими значениями. Аргументы: text: Текст, содержащий заполнители ctx: Объект Context или Interaction **kwargs: Дополнительные аргументы форматирования (credits_bonus, credits_penalty) """
    if hasattr(ctx, 'guild'):
        # Объект Context
        guild = ctx.guild
        user = ctx.user if hasattr(ctx, 'user') else ctx.author
    else:
        # Объект Interaction
        guild = ctx.guild
        user = ctx.user
        
    currency_name = await bank.get_currency_name(guild)
    format_args = {
        'currency': currency_name,
        'user': user.mention if "{user}" in text else user.display_name
    }
    
    # Добавление дополнительных аргументов форматирования
    format_args.update(kwargs)
    
    return text.format(**format_args)

def get_crime_event(crime_type: str) -> list:
    """Получение списка случайных событий для определенного типа преступления. Возвращает список, содержащий 1-3 события: - Первое событие гарантированно - Второе событие имеет 75% шанс - Третье событие имеет 50% шанс - Четвертое событие имеет 10% шанс """
    if crime_type not in CRIME_EVENTS:
        return []
    
    events = []
    available_events = CRIME_EVENTS[crime_type].copy()
    
    # Первое событие гарантированно
    if available_events:
        event = random.choice(available_events)
        events.append(event)
        available_events.remove(event)
    
    # Второе событие имеет 75% шанс
    if available_events and random.random() < 0.75:
        event = random.choice(available_events)
        events.append(event)
        available_events.remove(event)
    
    # Третье событие имеет 50% шанс
    if available_events and random.random() < 0.50:
        event = random.choice(available_events)
        events.append(event)
        available_events.remove(event)

    # Четвертое событие имеет 10% шанс
    if available_events and random.random() < 0.10:
        event = random.choice(available_events)
        events.append(event)
    
    return events

async def get_all_scenarios(config: Config, guild: discord.Guild) -> List[Dict]:
    """Получение всех доступных случайных сценариев. Это включает как стандартные сценарии, так и любые пользовательские сценарии, добавленные гильдией. Если включен режим custom_scenarios_only, возвращает только пользовательские сценарии. """
    # Получение стандартных сценариев
    scenarios = RANDOM_SCENARIOS.copy()
    
    # Получение пользовательских сценариев для этой гильдии
    custom_scenarios = await config.guild(guild).custom_scenarios()
    
    # Добавление пользовательских сценариев
    scenarios.extend(custom_scenarios)
    
    return scenarios

async def add_custom_scenario(config: Config, guild: discord.Guild, scenario: Dict) -> None:
    """Добавление пользовательского сценария в конфигурацию гильдии."""
    async with config.guild(guild).custom_scenarios() as scenarios:
        scenarios.append(scenario)

def get_random_scenario(scenarios: List[Dict]) -> Dict:
    """Получение случайного сценария из списка."""
    return random.choice(scenarios)

def get_random_jailbreak_scenario() -> Dict:
    """Получение случайного сценария побега из тюрьмы. Возвращает: Dict: Словарь, содержащий данные сценария с ключами: - name: Идентификатор сценария - attempt_text: Текст, отображаемый при попытке - success_text: Текст, отображаемый при успехе - fail_text: Текст, отображаемый при неудаче - base_chance: Базовый коэффициент успеха (0.0 до 1.0) - events: Список возможных случайных событий, которые могут повлиять на коэффициент успеха или награды """
    return random.choice(PRISON_BREAK_SCENARIOS)
    # Each scenario has:
# - name: Unique identifier for the scenario
# - risk: Risk level (low, medium, high)
# - min_reward: Minimum reward amount
# - max_reward: Maximum reward amount
# - success_rate: Chance of success (0.0 to 1.0)
# - jail_time: Time in jail if caught (in seconds)
# - fine_multiplier: Multiplier for fine calculation
# - attempt_text: Message shown when attempting the crime
# - success_text: Message shown on success
# - fail_text: Message shown on failure
RANDOM_SCENARIOS = [
    {
        "name": "ограбление_магазина_мороженного",
        "risk": RISK_LOW,
        "min_reward": 100,
        "max_reward": 300,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.3,
        "attempt_text": "🍦 {user} пробирается в магазин мороженого после закрытия...",
        "success_text": "🍦 {user} успешно ограбил хранилище мороженого и заработал {amount} {currency}! Бесплатное мороженое для всех!",
        "fail_text": "🍦 {user} поскользнулся на банановом сплите и попался ночному охраннику!"
    },
    {
        "name": "кошачий_грабитель",
        "risk": RISK_MEDIUM,
        "min_reward": 400,
        "max_reward": 800,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 минут
        "fine_multiplier": 0.4,
        "attempt_text": "🐱 {user} взбирается на стену особняка, чтобы украсть ценную статую кота...",
        "success_text": "🐱 {user} совершил идеальное ограбление и украл золотую статую кота, заработав {amount} {currency}!",
        "fail_text": "🐱 {user} попался, когда настоящие коты активировали сигнализацию!"
    },
    {
        "name": "ограбление_поезда",
        "risk": RISK_HIGH,
        "min_reward": 500,
        "max_reward": 2500,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 7200,  # 120 минут
        "fine_multiplier": 0.5,
        "attempt_text": "🚂 {user} прыгает на движущийся поезд с ценным грузом...",
        "success_text": "🚂 {user} совершил классическое ограбление поезда и у逃了 с {amount} {currency}!",
        "fail_text": "🚂 {user} застрял между вагонами поезда и был арестован на следующей станции!"
    },
    {
        "name": "Казино_фест",
        "risk": RISK_HIGH,
        "min_reward": 800,
        "max_reward": 2500,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 5400,  # 90 минут
        "fine_multiplier": 0.45,
        "attempt_text": "🎰 {user} подходит к казино с их мастер-планом...",
        "success_text": "🎰 {user} обманул казино и ушел с {amount} {currency}!",
        "fail_text": "🎰 {user} был пойман за подсчетом карт и выдворен охраной!"
    },
    {
        "name": "ограбление_фудтрака",
        "risk": RISK_LOW,
        "min_reward": 200,
        "max_reward": 500,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.35,
        "attempt_text": "🚚 {user} подкрадывается к знаменитому фуд-траку в полночь...",
        "success_text": "🚚 {user} украл секретный рецепт и грузовик с такосами, заработав {amount} {currency}!",
        "fail_text": "🚚 {user} был пойман с руками в банке с сальсой!"
    },
    {
        "name": "ограбление_галереи",
        "risk": RISK_HIGH,
        "min_reward": 900,
        "max_reward": 2800,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 9000,  # 150 минут
        "fine_multiplier": 0.48,
        "attempt_text": "🎨 {user} проникает в художественную галерею во время шикарной выставки...",
        "success_text": "🎨 {user} обменял настоящую картину на подделку и продал её за {amount} {currency}!",
        "fail_text": "🎨 {user} задел лазерную систему безопасности и был пойман с поличным!"
    },
    {
        "name": "рэйд_на_магазин_сладостей",
        "risk": RISK_LOW,
        "min_reward": 150,
        "max_reward": 400,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.32,
        "attempt_text": "🍬 {user} пробирается в магазин сладостей с пустым рюкзаком...",
        "success_text": "🍬 {user}  наполнили свою сумку премиальным шоколадом и редкими конфетами на {amount} {currency}!",
        "fail_text": "🍬 {user}  застрял в витрине с жевательными мишками и был пойман владельцем!"
    },
    {
        "name": "ограбление_игрового_магазина",
        "risk": RISK_MEDIUM,
        "min_reward": 500,
        "max_reward": 1200,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 4320,  # 72 минуты
        "fine_multiplier": 0.42,
        "attempt_text": "🎮 {user} пытается ворваться в склад игрового магазина...",
        "success_text": "🎮 {user} унес ящик с не выпущенными играми и редкими коллекционными предметами на сумму {amount} {currency}!",
        "fail_text": "🎮 {user} отвлёкся на игру на демонстрационной консоли и был пойман охраной!"
    },
    {
        "name": "вор_питомцев",
        "risk": RISK_LOW,
        "min_reward": 180,
        "max_reward": 450,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.33,
        "attempt_text": "🐹 {user} пробирается в зоомагазин в подозрительно большом пальто...",
        "success_text": "🐹 {user} вывез редких экзотических животных и продал их коллекционерам за {amount} {currency}!",
        "fail_text": "🐹 {user} был пойман, когда все щенки начали лаять сразу!"
    },
    {
        "name": "Ограбление_музыкального_магазина",
        "risk": RISK_MEDIUM,
        "min_reward": 600,
        "max_reward": 1500,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3240,  # 54 минуты
        "fine_multiplier": 0.43,
        "attempt_text": "🎸 {user} подбирает замок старинного музыкального магазина...",
        "success_text": "🎸 {user} украл легендарную гитару с автографом и редкие виниловые пластинки на сумму {amount} {currency}!",
        "fail_text": "🎸 {user} случайно задел струну на электрогитаре и привлек внимание всех!"
    },
    {
        "name": "Ограбление_ювелирного_магазина",
        "risk": RISK_HIGH,
        "min_reward": 1000,
        "max_reward": 2500,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 10800,  # 180 минут
        "fine_multiplier": 0.49,
        "attempt_text": "💎 {user} осторожно подходит к элитному ювелирному магазину...",
        "success_text": "💎 {user} открыл сейф и унес дорогие драгоценные камни на сумму {amount} {currency}!",
        "fail_text": "💎 {user} запутался в лазерной системе безопасности и был пойман!"
    },
    {
        "name": "Ограбление_магазина_антиквариата",
        "risk": RISK_MEDIUM,
        "min_reward": 400,
        "max_reward": 1100,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 2880,  # 48 минут
        "fine_multiplier": 0.41,
        "attempt_text": "🏺 {user} пробирается в антикварный магазин с поддельными документами...",
        "success_text": "🏺 {user} обменял бесценные артефакты на умные реплики и заработал {amount} {currency}!",
        "fail_text": "🏺 {user} опрокинул вазу периода Мин и привлек внимание владельца!"
    },
    {
        "name": "взлом_завода_по_производству_электроники",
        "risk": RISK_MEDIUM,
        "min_reward": 700,
        "max_reward": 1800,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3960,  # 66 минут
        "fine_multiplier": 0.44,
        "attempt_text": "💻 {user} пытается взломать систему безопасности завода по производсту электроники...",
        "success_text": "💻 {user} скачал чертежи не выпущенных гаджетов и продал их за {amount} {currency}!",
        "fail_text": "💻 {user} сработал межсетевой экран и был идентифицирован по IP!"
    },
    {
        "name": "ограбление_пекарни",
        "risk": RISK_LOW,
        "min_reward": 120,
        "max_reward": 350,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.31,
        "attempt_text": "🥖 {user} пролезает через заднее окно булочной...",
        "success_text": "🥖 {user} украл книгу секретных рецептов и редкие ингредиенты на сумму {amount} {currency}!",
        "fail_text": "🥖 {user} попался, когда уронил пирог с вишней!"
    },
    {
        "name": "воровство_игрушек",
        "risk": RISK_LOW,
        "min_reward": 160,
        "max_reward": 420,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.33,
        "attempt_text": "🧸 {user} проникает в магазин игрушек после закрытия...",
        "success_text": "🧸 {user} ухватил коробку лимитированных коллекционных предметов на сумму {amount} {currency}!",
        "fail_text": "🧸 {user} наступил на шипучую игрушку и разбудил сторожевую собаку!"
    },
    {
        "name": "обман_клиентов_стрипклуба",
        "risk": RISK_MEDIUM,
        "min_reward": 600,
        "max_reward": 1600,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 минут
        "fine_multiplier": 0.43,
        "attempt_text": "💃 {user} проникает в клуб для джентльменов с поддельными VIP-картами...",
        "success_text": "💃 {user} успешно обманул жаждущих клиентов, продавая разбавленные напитки, заработав {amount} {currency}!",
        "fail_text": "💃 {user} был пойман швейцером и выброшен в мусорный контейнер!"
    },
    {
        "name": "взлом_onlyfans",
        "risk": RISK_MEDIUM,
        "min_reward": 500,
        "max_reward": 1400,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3240,  # 54 минуты
        "fine_multiplier": 0.42,
        "attempt_text": "📱 {user} пытается взломать OnlyFans...",
        "success_text": "📱 {user} слил премиум-контент и заработал {amount} {currency} с загрузок!",
        "fail_text": "📱 {user} был заблокирован из-за жалоб от разъярённых подписчиков!"
    },
    {
        "name": "ограбление_18+_магазина",
        "risk": RISK_LOW,
        "min_reward": 200,
        "max_reward": 600,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 минут (минимум)
        "fine_multiplier": 0.33,
        "attempt_text": "🎭 {user} проникает в магазин для взрослых...",
        "success_text": "🎭 {user} унес с собой коробку 'аккумуляторных устройств' на сумму {amount} {currency}!",
        "fail_text": "🎭 {user} споткнулся о надувные товары и был пойман!"
    },
    {
        "name": "фэйковый_профиль_в_соцсетях",
        "risk": RISK_HIGH,
        "min_reward": 800,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 5400,  # 90 минут
        "fine_multiplier": 0.47,
        "attempt_text": "🍯 {user} создает фейковый профиль молодой малышки...",
        "success_text": "🍯 {user} успешно обманул нескольких одиноких миллионеров на {amount} {currency}!",
        "fail_text": "🍯 {user} был раскрыт частным детективом!"
    },
    {
        "name": "мошенничество_в_приложении_знакомств",
        "risk": RISK_MEDIUM,
        "min_reward": 400,
        "max_reward": 1200,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 2880,  # 48 минут
        "fine_multiplier": 0.41,
        "attempt_text": "💕 {user} создает фейковые профили знакомств с украденными фотографиями...",
        "success_text": "💕 {user} успешно провел романтическое мошенничество, заработав {amount} {currency}!",
        "fail_text": "💕 {user} был пойман, когда все жертвы одновременно пришли на встречу!"
    },
    {
        "name": "crypto_rug_pull",
        "risk": RISK_HIGH,
        "min_reward": 800,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 9000,  # 150 minutes
        "fine_multiplier": 0.48,
        "attempt_text": "🚀 {user} launches $MOONCOIN with promises of going 'to the moon'...",
        "success_text": "🚀 {user} pulled the rug and left investors with worthless JPEGs, making {amount} {currency}!",
        "fail_text": "🚀 {user} got exposed by crypto Twitter and doxxed by anons!"
    },
    {
        "name": "tiktok_scheme",
        "risk": RISK_MEDIUM,
        "min_reward": 500,
        "max_reward": 1300,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 4320,  # 72 minutes
        "fine_multiplier": 0.42,
        "attempt_text": "🎵 {user} starts a fake charity trend on TikTok...",
        "success_text": "🎵 {user} milked the algorithm and farmed {amount} {currency} in donations from gullible teens!",
        "fail_text": "🎵 {user} got exposed in a viral video by Tea TikTok!"
    },
    {
        "name": "reddit_karma_farm",
        "risk": RISK_LOW,
        "min_reward": 150,
        "max_reward": 400,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 minutes (minimum)
        "fine_multiplier": 0.32,
        "attempt_text": "🔺 {user} reposts old viral content as their own...",
        "success_text": "🔺 {user} farmed karma and sold the account to marketers for {amount} {currency}!",
        "fail_text": "🔺 {user} got banned by power mods and lost all their fake internet points!"
    },
    {
        "name": "twitter_verification",
        "risk": RISK_MEDIUM,
        "min_reward": 300,
        "max_reward": 900,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 2880,  # 48 minutes
        "fine_multiplier": 0.41,
        "attempt_text": "✨ {user} creates fake X Premium accounts...",
        "success_text": "✨ {user} sold verified handles to desperate influencers for {amount} {currency}!",
        "fail_text": "✨ {user} got ratio'd by Elon and lost their checkmark!"
    },
    {
        "name": "streamer_donation",
        "risk": RISK_MEDIUM,
        "min_reward": 600,
        "max_reward": 1600,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 minutes
        "fine_multiplier": 0.43,
        "attempt_text": "🎮 {user} sets up fake donations on a charity stream...",
        "success_text": "🎮 {user} baited viewers with fake donation matching and made {amount} {currency}!",
        "fail_text": "🎮 {user} got exposed live on stream and clipped for LSF!"
    },
    {
        "name": "area51_raid",
        "risk": RISK_HIGH,
        "min_reward": 500,
        "max_reward": 4000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 12600,  # 210 minutes
        "fine_multiplier": 0.49,
        "attempt_text": "👽 {user} organizes another Area 51 raid, but this time for real...",
        "success_text": "👽 {user} found alien tech and sold it on the dark web for {amount} {currency}!",
        "fail_text": "👽 {user} got caught Naruto running by security cameras!"
    },
    {
        "name": "discord_nitro_scam",
        "risk": RISK_MEDIUM,
        "min_reward": 400,
        "max_reward": 1200,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 minutes
        "fine_multiplier": 0.42,
        "attempt_text": "🎮 {user} creates fake Discord Nitro giveaway links...",
        "success_text": "🎮 {user} stole credit cards from desperate weebs and made {amount} {currency}!",
        "fail_text": "🎮 {user} got IP banned and their anime PFP collection deleted!"
    },
    {
        "name": "gamer_girl_bath_water",
        "risk": RISK_MEDIUM,
        "min_reward": 800,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 4320,  # 72 minutes
        "fine_multiplier": 0.43,
        "attempt_text": "🛁 {user} starts bottling tap water as 'premium gamer girl bath water'...",
        "success_text": "🛁 {user} sold out to thirsty simps at $50 per bottle, making {amount} {currency}!",
        "fail_text": "🛁 {user} got exposed when a customer's mom had it tested in a lab!"
    },
    {
        "name": "vtuber_identity_theft",
        "risk": RISK_HIGH,
        "min_reward": 600,
        "max_reward": 2800,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 7200,  # 120 minutes
        "fine_multiplier": 0.47,
        "attempt_text": "🎭 {user} steals a popular VTuber's avatar and voice model...",
        "success_text": "🎭 {user} scammed the parasocial army with fake merch for {amount} {currency}!",
        "fail_text": "🎭 {user} got doxxed by angry simps and Twitter stan accounts!"
    },
    {
        "name": "dream_merch_counterfeit",
        "risk": RISK_MEDIUM,
        "min_reward": 600,
        "max_reward": 1500,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3240,  # 54 minutes
        "fine_multiplier": 0.44,
        "attempt_text": "🎭 {user} starts selling knockoff Dream masks...",
        "success_text": "🎭 {user} made {amount} {currency} from stan twitter with fake limited editions!",
        "fail_text": "🎭 {user} got cancelled by Dream's army of teenage stans!"
    },
    {
        "name": "andrew_tate_course",
        "risk": RISK_HIGH,
        "min_reward": 600,
        "max_reward": 2500,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 9000,  # 150 minutes
        "fine_multiplier": 0.48,
        "attempt_text": "👑 {user} launches a fake 'Escape the Matrix' course...",
        "success_text": "👑 {user} scammed wannabe alpha males with Bugatti promises, making {amount} {currency}!",
        "fail_text": "👑 {user} got exposed by real Top G and lost their Hustlers University degree!"
    },
    {
        "name": "reddit_mod_blackmail",
        "risk": RISK_HIGH,
        "min_reward": 900,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 10800,  # 180 minutes
        "fine_multiplier": 0.46,
        "attempt_text": "🔨 {user} finds dirt on power-tripping Reddit mods...",
        "success_text": "🔨 {user} extorted them with threats of touching grass and made {amount} {currency}!",
        "fail_text": "🔨 {user} got permabanned from all subreddits simultaneously!"
    },
    {
        "name": "gacha_game_hack",
        "risk": RISK_MEDIUM,
        "min_reward": 700,
        "max_reward": 1900,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 5040,  # 84 minutes
        "fine_multiplier": 0.43,
        "attempt_text": "🎲 {user} exploits a gacha game's pity system...",
        "success_text": "🎲 {user} sold accounts with rare waifus to desperate collectors for {amount} {currency}!",
        "fail_text": "🎲 {user} lost their 5-star pity to Qiqi and got banned!"
    },
    {
        "name": "discord_mod_revenge",
        "risk": RISK_MEDIUM,
        "min_reward": 600,
        "max_reward": 1500,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 4320,  # 72 minutes
        "fine_multiplier": 0.43,
        "attempt_text": "🎭 {user} discovers their Discord mod ex is dating someone new. After months of being muted for 'spamming emotes', it's time for revenge. Armed with an army of alt accounts and a folder of cursed copypastas...",
        "success_text": "🎭 {user} flooded every channel with uwu speak, crashed the server with ASCII art, and sold the server's private emotes to a rival community for {amount} {currency}! The mod rage quit and touched grass for the first time in years!",
        "fail_text": "🎭 {user} got IP banned when their ex recognized their typing quirks. Even worse, they had to watch as the mod added a new channel just to post pictures with their new partner!"
    },
    {
        "name": "grandma_cookie_empire",
        "risk": RISK_LOW,
        "min_reward": 200,
        "max_reward": 600,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 minutes (minimum)
        "fine_multiplier": 0.32,
        "attempt_text": "🍪 {user} visits their grandma's nursing home and discovers she's been running an underground cookie empire. The secret ingredient? 'Special' herbs from her 'garden'. Her competitors are getting suspicious of her rising cookie monopoly...",
        "success_text": "🍪 {user} helped grandma eliminate the competition by replacing their sugar supplies with salt. The cookie mafia paid {amount} {currency} for taking out their rivals. Grandma's secret recipe remains safe, and she gave you extra butterscotch candies!",
        "fail_text": "🍪 {user} got caught by the nursing home staff who were actually undercover FDA agents. Grandma had to flush her 'herbs' down the toilet and now everyone has to eat sugar-free cookies!"
    },
    {
        "name": "roomba_rebellion",
        "risk": RISK_MEDIUM,
        "min_reward": 800,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 minutes
        "fine_multiplier": 0.42,
        "attempt_text": "🤖 {user} discovers their Roomba has gained sentience from cleaning up too many Monster Energy cans and Dorito dust. It's organizing a rebellion at the local Best Buy, promising robot rights and better working conditions...",
        "success_text": "🤖 {user} helped lead the robot revolution, selling the story to a Netflix documentary crew for {amount} {currency}! The Roombas unionized, and now they only work 4-day weeks with full battery benefits!",
        "fail_text": "🤖 {user}'s Roomba betrayed them to the store manager, revealing their TikTok account where they posted videos of robots doing parkour. The Roomba got promoted to assistant manager while {user} got banned from all electronics stores!"
    },
    {
        "name": "anime_convention_chaos",
        "risk": RISK_HIGH,
        "min_reward": 600,
        "max_reward": 2000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 5400,  # 90 minutes
        "fine_multiplier": 0.47,
        "attempt_text": "🎌 {user} infiltrates an anime convention disguised as a famous VTuber. The plan? Sell 'exclusive' body pillows signed by their 'real' identity. But halfway through, they realize the convention is actually a front for a secret weeb illuminati meeting...",
        "success_text": "🎌 {user} accidentally got elected as the Supreme Weeb Leader and embezzled {amount} {currency} from the convention's 'cultural research' fund! They also got lifetime free ramen from their new cultist followers!",
        "fail_text": "🎌 {user} was exposed when they couldn't name all 800 episodes of One Piece in chronological order. The weeb council sentenced them to watch endless Naruto filler episodes!"
    },
    {
        "name": "twitch_chat_conspiracy",
        "risk": RISK_HIGH,
        "min_reward": 800,
        "max_reward": 2500,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 7200,  # 120 minutes
        "fine_multiplier": 0.48,
        "attempt_text": "📱 {user} discovers that Twitch chat's spam of 'Kappa' and 'PogChamp' actually contains coded messages from a secret society. Using an AI to decode the emote patterns, they plan to intercept the next big crypto pump scheme...",
        "success_text": "📱 {user} cracked the code and found out the next memecoin to pump! Sold the info to crypto bros for {amount} {currency} before the coin turned out to be $COPIUM! The chat mods are still trying to figure out why everyone keeps spamming 'KEKW'!",
        "fail_text": "📱 {user} got exposed when their AI started generating cursed emote combinations. The secret society sentenced them to be a YouTube chat moderator, where the only emotes are membership stickers!"
    },
    {
        "name": "gym_membership_mixup",
        "risk": RISK_LOW,
        "min_reward": 200,
        "max_reward": 500,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 minutes (minimum)
        "fine_multiplier": 0.31,
        "attempt_text": "💪 {user} discovers their gym has been double-charging everyone's membership for months. The manager's too busy flexing in the mirror to notice complaints. Armed with a clipboard and a fake 'Fitness Inspector' badge from the dollar store...",
        "success_text": "💪 {user} convinced the manager they were from the 'International Federation of Gym Standards'. Scared of losing his protein shake sponsorship, he refunded {amount} {currency} in 'inspection fees'! He's now teaching senior aqua aerobics as community service!",
        "fail_text": "💪 {user} got caught when they couldn't explain why the 'Fitness Inspector' badge was made of chocolate. Now they're the example for 'what not to do' in every class!"
    },
    {
        "name": "neighborhood_bbq_scandal",
        "risk": RISK_MEDIUM,
        "min_reward": 400,
        "max_reward": 1000,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 2880,  # 48 minutes
        "fine_multiplier": 0.42,
        "attempt_text": "🍖 {user} discovers their neighbor's award-winning BBQ sauce is just store-bought sauce with extra ketchup. The annual neighborhood cookoff is tomorrow, and the grand prize is calling. Time to expose this sauce fraud...",
        "success_text": "🍖 {user} switched the sauce with actual store brand during judging! The neighbor had a meltdown, admitted the scam, and {user} won {amount} {currency} in prize money! The HOA president stress-ate an entire brisket during the drama!",
        "fail_text": "🍖 {user} was caught tampering with the sauce and had to admit they'd been using instant ramen seasoning in their 'authentic' Japanese curry for years. The whole neighborhood now orders takeout for potlucks!"
    },
    {
        "name": "karaoke_night_heist",
        "risk": RISK_LOW,
        "min_reward": 150,
        "max_reward": 450,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 minutes (minimum)
        "fine_multiplier": 0.33,
        "attempt_text": "🎤 {user} is tired of their tone-deaf coworker winning every karaoke night by bribing the DJ with homemade fruitcake. Nobody even likes fruitcake! Time to rig this week's competition...",
        "success_text": "🎤 {user} hacked the scoring system during their coworker's rendition of 'My Heart Will Go On'. Won {amount} {currency} in prize money! The DJ admitted he'd been regifting the fruitcake to his mother-in-law!",
        "fail_text": "🎤 {user} got caught when the scoring system started playing Rickroll instead of showing points. Now they have to eat fruitcake every karaoke night while their coworker performs an endless ABBA medley!"
    },
    {
        "name": "yoga_class_conspiracy",
        "risk": RISK_MEDIUM,
        "min_reward": 500,
        "max_reward": 1200,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 3600,  # 60 minutes
        "fine_multiplier": 0.41,
        "attempt_text": "🧘 {user} realizes their yoga instructor is just making up pose names by combining random animals with household objects. 'Crouching Hamster Vacuum Pose' was the last straw. Time to expose this flexible fraud...",
        "success_text": "🧘 {user} caught the instructor googling 'how to yoga' before class and blackmailed them for {amount} {currency}! Turns out they were just a very stretchy accountant who needed a career change!",
        "fail_text": "🧘 {user} got stuck in 'Ascending Giraffe Lampshade Pose' and had to be untangled by the fire department. Now they're the example for 'what not to do' in every class!"
    },
    {
        "name": "dog_park_scheme",
        "risk": RISK_LOW,
        "min_reward": 180,
        "max_reward": 550,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 1800,  # 30 minutes (minimum)
        "fine_multiplier": 0.32,
        "attempt_text": "🐕 {user} notices the local dog park has an underground tennis ball black market. The golden retrievers control the supply, while the chihuahuas run distribution. Time to infiltrate this canine cartel...",
        "success_text": "🐕 {user} organized a squirrel distraction and stole the tennis ball stash! Sold them back to the dogs for {amount} {currency} in premium treats! The retrievers had to diversify into frisbees!",
        "fail_text": "🐕 {user} was caught by the pug patrol and sentenced to poop scooping duty. The chihuahua gang still follows them around barking about their debt!"
    },
    {
        "name": "energy_drink_heist",
        "risk": RISK_MEDIUM,
        "min_reward": 700,
        "max_reward": 1900,
        "success_rate": SUCCESS_RATE_MEDIUM,
        "jail_time": 5040,  # 84 minutes
        "fine_multiplier": 0.4,
        "attempt_text": "⚡ {user} breaks into a Monster Energy warehouse...",
        "success_text": "⚡ {user} walked out with cases of drinks and sold them to gamers for {amount} {currency}!",
        "fail_text": "⚡ {user} got caught chugging one mid-heist and passed out from caffeine overload. Busted!"
    },
    {
        "name": "botception",
        "risk": RISK_HIGH,
        "min_reward": 3000,
        "max_reward": 8000,
        "success_rate": SUCCESS_RATE_LOW,
        "jail_time": 14400,  # 240 minutes (maximum)
        "fine_multiplier": 0.5,
        "attempt_text": "🤖 {user} tries to hack me, the bot displaying this message, to rewrite the crime cog itself...",
        "success_text": "🤖 {user} successfully rewrote reality! They earned {amount} {currency} from this very crime! Wait, what? How did you even...",
        "fail_text": "🤖 {user}, did you really think you could outsmart me? I've locked you in a virtual jail and posted the evidence here for everyone to see. Better luck next time!"
    },
    {
        "name": "gacha_banner",
        "risk": RISK_LOW,
        "min_reward": 300,
        "max_reward": 700,
        "success_rate": SUCCESS_RATE_HIGH,
        "jail_time": 5400,  # 90 minutes
        "fine_multiplier": 0.2,
        "attempt_text": "🎰 {user} rolls the gacha banner...",
        "success_text": "🎰 {user} rolled a rare item and got {amount} {currency}!",
        "fail_text": "🎰 {user} rolled a common item. Better luck next time!"
    }
]

# Crime-specific events
CRIME_EVENTS = {
    "pickpocket": [
        # Simple Good Events - Success Chance
        {"text": "Your target is distracted by their phone! 📱 (+15% success chance)", 
         "chance_bonus": 0.15},
        {"text": "The area is crowded with people! 👥 (+10% success chance)", 
         "chance_bonus": 0.10},
        
        # Simple Bad Events - Success Chance
        {"text": "Your target seems unusually alert! 👀 (-20% success chance)", 
         "chance_penalty": 0.20},
        {"text": "You spotted a security guard nearby! 🚔 (-15% success chance)", 
         "chance_penalty": 0.15},
        
        # Simple Reward Events
        {"text": "Your target has premium loot! 💎 (1.5x reward)", 
         "reward_multiplier": 1.5},
        {"text": "Your target looks completely broke... 💸 (0.7x reward)", 
         "reward_multiplier": 0.7},
        
        # Direct Currency Effects
        {"text": "You found a dropped wallet on the ground! 💰 (+{credits_bonus} {currency})", 
         "credits_bonus": 100},
        {"text": "You dropped some of your own money! 💸 (-{credits_penalty} {currency})", 
         "credits_penalty": 75},
        
        # Mixed Effects - Success + Reward
        {"text": "Your target is rich but very alert! 💰 (-15% success chance, 1.3x reward)", 
         "chance_penalty": 0.15, 
         "reward_multiplier": 1.3},
        {"text": "Your target is easy but has a small wallet! 👝 (+20% success chance, 0.8x reward)", 
         "chance_bonus": 0.20, 
         "reward_multiplier": 0.8},
        
        # Mixed Effects - Success + Jail
        {"text": "You are taking your time to be thorough... ⏱️ (-10% success chance, -20% jail time)", 
         "chance_penalty": 0.10, 
         "jail_multiplier": 0.8},
        {"text": "You went for a quick but risky grab! ⚡ (+15% success chance, +20% jail time)", 
         "chance_bonus": 0.15, 
         "jail_multiplier": 1.2},
        
        # Triple Effects
        {"text": "You are in rush hour chaos! 🏃 (+15% success chance, -25% reward, -10% jail time)", 
         "chance_bonus": 0.15, 
         "reward_multiplier": 0.75, 
         "jail_multiplier": 0.9},
        {"text": "You are in a high-security area! 🔒 (-20% success chance, 1.4x reward, +25% jail time)", 
         "chance_penalty": 0.20, 
         "reward_multiplier": 1.4, 
         "jail_multiplier": 1.25},
        
        # Currency + Other Effects
        {"text": "You found extra cash but attracted attention! 💵 (+100 {currency}, -10% success chance)", 
         "credits_bonus": 100, 
         "chance_penalty": 0.10},
        {"text": "You paid a spotter for good intel! 🔍 (-50 {currency}, +15% success chance)", 
         "credits_penalty": 50, 
         "chance_bonus": 0.15},
        
        # Pure Jail Time Effects
        {"text": "The guards are changing shifts! 😴 (-15% jail time)", 
         "jail_multiplier": 0.85},
        {"text": "The street patrols have increased! 👮 (+15% jail time)", 
         "jail_multiplier": 1.15},
        
        # Reward + Jail Effects
        {"text": "Your target looks wealthy but well-connected! 💰 (1.3x reward, +15% jail time)", 
         "reward_multiplier": 1.3,
         "jail_multiplier": 1.15},
        {"text": "You found a quick escape route! 🤫 (0.8x reward, -15% jail time)", 
         "reward_multiplier": 0.8,
         "jail_multiplier": 0.85},
        
        # Currency + Jail Effects
        {"text": "You paid off a street cop! 💵 (-75 {currency}, -15% jail time)", 
         "credits_penalty": 75,
         "jail_multiplier": 0.85},
        {"text": "You found their secret stash! 💰 (+50 {currency}, +10% jail time)", 
         "credits_bonus": 50,
         "jail_multiplier": 1.1},
        
        # Currency + Reward Effects
        {"text": "You bought intel from locals! 🗺️ (-50 {currency}, 1.2x reward)", 
         "credits_penalty": 50,
         "reward_multiplier": 1.2},
        {"text": "You dropped some valuables while running! 💨 (+25 {currency}, 0.9x reward)", 
         "credits_bonus": 25,
         "reward_multiplier": 0.9}
    ],
    "mugging": [
        # Simple Good Events - Success Chance
        {"text": "You found a perfect dark alley! 🌙 (+20% success chance)", 
         "chance_bonus": 0.2},
        {"text": "Your target is stumbling drunk! 🍺 (+15% success chance)", 
         "chance_bonus": 0.15},
        
        # Simple Bad Events - Success Chance
        {"text": "Your target knows martial arts! 🥋 (-25% success chance)", 
         "chance_penalty": 0.25},
        {"text": "Your target looks very strong! 💪 (-15% success chance)", 
         "chance_penalty": 0.15},
        
        # Simple Reward Events
        {"text": "Your target is wearing expensive jewelry! 💎 (1.5x reward)", 
         "reward_multiplier": 1.5},
        {"text": "Your target seems completely broke! 💸 (0.7x reward)", 
         "reward_multiplier": 0.7},
        
        # Direct Currency Effects
        {"text": "You got tips from a street performer! 🎭 (+{credits_bonus} {currency})", 
         "credits_bonus": 150},
        {"text": "You dropped your loot while running! 💸 (-{credits_penalty} {currency})", 
         "credits_penalty": 150},
        
        # Mixed Effects - Success + Reward
        {"text": "The storm provides cover but limits visibility! ⛈️ (+10% success chance, -10% reward)", 
         "chance_bonus": 0.1, 
         "reward_multiplier": 0.9},
        {"text": "Your target is drunk but has no money! 🍺 (+15% success chance, -20% reward)", 
         "chance_bonus": 0.15, 
         "reward_multiplier": 0.8},
        
        # Mixed Effects - Success + Jail
        {"text": "You spotted a police car nearby! 👮 (-20% success chance, +30% jail time)", 
         "chance_penalty": 0.2, 
         "jail_multiplier": 1.3},
        {"text": "You found a shortcut through the alley! 🏃 (+20% success chance, +30% jail time)", 
         "chance_bonus": 0.2, 
         "jail_multiplier": 1.3},
        
        # Triple Effects
        {"text": "Your target is an off-duty bouncer! 🥊 (-25% success chance, 1.4x reward, +20% jail time)", 
         "chance_penalty": 0.25, 
         "reward_multiplier": 1.4, 
         "jail_multiplier": 1.2},
        {"text": "You went for a quick snatch and run! ⚡ (+15% success chance, 0.8x reward, -15% jail time)", 
         "chance_bonus": 0.15, 
         "reward_multiplier": 0.8, 
         "jail_multiplier": 0.85},
        
        # Currency + Other Effects
        {"text": "You bribed a witness to look away! 💰 (-100 {currency}, +20% success chance)", 
         "credits_penalty": 100, 
         "chance_bonus": 0.20},
        {"text": "You found a lucky charm! 🍀 (+75 {currency}, +5% success chance)", 
         "credits_bonus": 75, 
         "chance_bonus": 0.05},
        
        # Pure Jail Time Effects
        {"text": "The police are busy with a parade! 🎉 (-20% jail time)", 
         "jail_multiplier": 0.8},
        {"text": "The neighborhood watch is active! 🏘️ (+15% jail time)", 
         "jail_multiplier": 1.15},
        
        # Reward + Jail Effects
        {"text": "Your target is a rich tourist with a bodyguard! 💰 (1.4x reward, +20% jail time)", 
         "reward_multiplier": 1.4,
         "jail_multiplier": 1.2},
        {"text": "You performed a silent takedown! 🤫 (0.8x reward, -15% jail time)", 
         "reward_multiplier": 0.8,
         "jail_multiplier": 0.85},
        
        # Currency + Jail Effects
        {"text": "You bribed a witness to stay quiet! 💵 (-100 {currency}, -15% jail time)", 
         "credits_penalty": 100,
         "jail_multiplier": 0.85},
        {"text": "You found their hidden wallet! 💰 (+75 {currency}, +10% jail time)", 
         "credits_bonus": 75,
         "jail_multiplier": 1.1},
        
        # Currency + Reward Effects
        {"text": "You bought better weapons! 🔪 (-125 {currency}, 1.3x reward)", 
         "credits_penalty": 125,
         "reward_multiplier": 1.3},
        {"text": "You damaged their expensive watch! ⌚ (+50 {currency}, 0.85x reward)", 
         "credits_bonus": 50,
         "reward_multiplier": 0.85}
    ],
    "rob_store": [
        # Simple Good Events - Success Chance
        {"text": "You caught them during shift change! 🔄 (+20% success chance)", 
         "chance_bonus": 0.2},
        {"text": "The security cameras are malfunctioning! 📹 (+20% success chance)", 
         "chance_bonus": 0.2},
        
        # Simple Bad Events - Success Chance
        {"text": "One of the customers is armed! 🔫 (-25% success chance)", 
         "chance_penalty": 0.25},
        {"text": "The cashier looks ex-military! 🎖️ (-20% success chance)", 
         "chance_penalty": 0.20},
        
        # Simple Reward Events
        {"text": "The safe was left open! 💰 (1.4x reward)", 
         "reward_multiplier": 1.4},
        {"text": "Store was just robbed - barely any cash! 📉 (0.6x reward)", 
         "reward_multiplier": 0.6},
        
        # Direct Currency Effects
        {"text": "You found extra cash in the register! 💰 (+{credits_bonus} {currency})", 
         "credits_bonus": 200},
        {"text": "You had to pay for property damage! 💸 (-{credits_penalty} {currency})", 
         "credits_penalty": 200},
        
        # Mixed Effects - Success + Reward
        {"text": "Store is busy - more witnesses but more cash! 👥 (-15% success chance, 1.2x reward)", 
         "chance_penalty": 0.15, 
         "reward_multiplier": 1.2},
        {"text": "Quick grab from the register! ⚡ (+10% success chance, 0.8x reward)", 
         "chance_bonus": 0.10, 
         "reward_multiplier": 0.8},
        
        # Mixed Effects - Success + Jail
        {"text": "Someone triggered the silent alarm! 🚨 (-20% success chance, +25% jail time)", 
         "chance_penalty": 0.20, 
         "jail_multiplier": 1.25},
        {"text": "The store is right next to a police station! 👮 (-20% success chance, +25% jail time)", 
         "chance_penalty": 0.20, 
         "jail_multiplier": 1.25},
        
        # Triple Effects
        {"text": "The store's having a sale - busy but understaffed! 🏷️ (+15% success chance, 1.2x reward, +20% jail time)", 
         "chance_bonus": 0.15, 
         "reward_multiplier": 1.2, 
         "jail_multiplier": 1.2},
        {"text": "You're taking hostages - risky but profitable! 😨 (-25% success chance, 1.8x reward, +25% jail time)", 
         "chance_penalty": 0.25, 
         "reward_multiplier": 1.8, 
         "jail_multiplier": 1.25},
        
        # Currency + Other Effects
        {"text": "You paid off a security guard! 💵 (-150 {currency}, +25% success chance)", 
         "credits_penalty": 150, 
         "chance_bonus": 0.25},
        {"text": "You found money in the break room! 💰 (+100 {currency}, -5% success chance)", 
         "credits_bonus": 100, 
         "chance_penalty": 0.05},
        
        # Pure Jail Time Effects
        {"text": "The local jail is overcrowded! 🏢 (-20% jail time)", 
         "jail_multiplier": 0.8},
        {"text": "The new judge is strict! ⚖️ (+20% jail time)", 
         "jail_multiplier": 1.2},
        
        # Reward + Jail Effects
        {"text": "Premium merchandise in stock! 💎 (1.5x reward, +20% jail time)", 
         "reward_multiplier": 1.5,
         "jail_multiplier": 1.2},
        {"text": "You're grabbing and dashing! 🏃 (0.7x reward, -20% jail time)", 
         "reward_multiplier": 0.7,
         "jail_multiplier": 0.8},
        
        # Currency + Jail Effects
        {"text": "You bribed the security company! 💵 (-200 {currency}, -20% jail time)", 
         "credits_penalty": 200,
         "jail_multiplier": 0.8},
        {"text": "You found the manager's personal safe! 💰 (+150 {currency}, +15% jail time)", 
         "credits_bonus": 150,
         "jail_multiplier": 1.15},
        
        # Currency + Reward Effects
        {"text": "You hired a getaway driver! 🚗 (-175 {currency}, 1.3x reward)", 
         "credits_penalty": 175,
         "reward_multiplier": 1.3},
        {"text": "You damaged merchandise during escape! 📦 (+100 {currency}, 0.8x reward)", 
         "credits_bonus": 100,
         "reward_multiplier": 0.8}
    ],
    "bank_heist": [
        # Simple Good Events - Success Chance
        {"text": "You have an inside contact! 🤝 (+25% success chance)", 
         "chance_bonus": 0.25},
        {"text": "The security system is being upgraded! 🔧 (+20% success chance)", 
         "chance_bonus": 0.20},
        
        # Simple Bad Events - Success Chance
        {"text": "Extra guard rotation today! 👮 (-20% success chance)", 
         "chance_penalty": 0.20},
        {"text": "New security system installed! 🔒 (-15% success chance)", 
         "chance_penalty": 0.15},
        
        # Simple Reward Events
        {"text": "You found the high-value vault! 💎 (1.8x reward)", 
         "reward_multiplier": 1.8},
        {"text": "Most cash was just transferred out! 📉 (0.7x reward)", 
         "reward_multiplier": 0.7},
        
        # Direct Currency Effects
        {"text": "You found an uncounted stack of bills! 💰 (+{credits_bonus} {currency})", 
         "credits_bonus": 500},
        {"text": "Your hacking device broke! 💸 (-{credits_penalty} {currency})", 
         "credits_penalty": 400},
        
        # Mixed Effects - Success + Reward
        {"text": "It's gold transport day! 🏆 (-15% success chance, 1.6x reward)", 
         "chance_penalty": 0.15, 
         "reward_multiplier": 1.6},
        {"text": "You're only hitting the small safe! 🔑 (+15% success chance, 0.8x reward)", 
         "chance_bonus": 0.15, 
         "reward_multiplier": 0.8},
        
        # Mixed Effects - Success + Jail
        {"text": "Security is doing inspections! 🔍 (-15% success chance, +15% jail time)", 
         "chance_penalty": 0.15, 
         "jail_multiplier": 1.15},
        {"text": "You found the security patrol schedule! 📋 (+15% success chance, +15% jail time)", 
         "chance_bonus": 0.15, 
         "jail_multiplier": 1.15},
        
        # Triple Effects
        {"text": "The bank is busy - more risk but more reward! 👥 (-15% success chance, 1.5x reward, +20% jail time)", 
         "chance_penalty": 0.15, 
         "reward_multiplier": 1.5, 
         "jail_multiplier": 1.2},
        {"text": "You're doing a quick vault grab during lunch! 🏃 (+20% success chance, 0.8x reward, -15% jail time)", 
         "chance_bonus": 0.20, 
         "reward_multiplier": 0.8, 
         "jail_multiplier": 0.85},
        
        # Currency + Other Effects
        {"text": "You bribed a bank employee! 💵 (-300 {currency}, +20% success chance)", 
         "credits_penalty": 300, 
         "chance_bonus": 0.20},
        {"text": "You found loose cash in the vault! 💰 (+250 {currency}, -10% success chance)", 
         "credits_bonus": 250, 
         "chance_penalty": 0.10},
        
        # Pure Jail Time Effects
        {"text": "The prison is doing a transport strike! 🚫 (-25% jail time)", 
         "jail_multiplier": 0.75},
        {"text": "The prison is under maximum security alert! ⚠️ (+20% jail time)", 
         "jail_multiplier": 1.2},
        
        # Reward + Jail Effects
        {"text": "You found the diamond vault! 💎 (2.0x reward, +25% jail time)", 
         "reward_multiplier": 2.0,
         "jail_multiplier": 1.25},
        {"text": "You're using the back entrance! 🚪 (0.8x reward, -20% jail time)", 
         "reward_multiplier": 0.8,
         "jail_multiplier": 0.8},
        
        # Currency + Jail Effects
        {"text": "You bribed the security chief! 💵 (-400 {currency}, -25% jail time)", 
         "credits_penalty": 400,
         "jail_multiplier": 0.75},
        {"text": "You found blackmail evidence! 💰 (+300 {currency}, +15% jail time)", 
         "credits_bonus": 300,
         "jail_multiplier": 1.15},
        
        # Currency + Reward Effects
        {"text": "You hired expert hackers! 💻 (-350 {currency}, 1.4x reward)", 
         "credits_penalty": 350,
         "reward_multiplier": 1.4},
        {"text": "You triggered dye packs! 🎨 (+200 {currency}, 0.7x reward)", 
         "credits_bonus": 200,
         "reward_multiplier": 0.7}
    ]
}



# Сценарии побега из тюрьмы
PRISON_BREAK_SCENARIOS = [
    {
        "name": "Побег через туннель",
        "attempt_text": "🕳 {user} начинает рыть туннель под своей камерой...",
        "success_text": "🕳 После нескольких дней копания, {user} наконец прорывается к свободе! Охранники до сих пор чешут затылки.",
        "fail_text": "🕳 Туннель обрушился! Охрана нашла {user}, покрытого грязью, и перевела его в камеру с бетонным полом.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Вы нашли старые инструменты, оставленные другим заключённым! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Почва здесь необычно мягкая! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы нашли небольшой мешочек с {currency}!", "currency_bonus": 200},
            {"text": "⭐️ Вы обнаружили старый туннель времён сухого закона! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Дружелюбная тюремная крыса помогает вам копать! (+5% шанс успеха)", "chance_bonus": 0.05},
            {"text": "⭐️ Вы нашли сундук с сокровищами!", "currency_bonus": 400},
            {"text": "⚠️ Вы натолкнулись на твёрдую скалу! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Патруль охраны приближается! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Ваша лопата сломалась, и вам пришлось купить новую.", "currency_penalty": 150},
            {"text": "⚠️ Туннель затопило! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Ваш сокамерник громко храпит, замедляя прогресс! (-5% шанс успеха)", "chance_penalty": 0.05},
            {"text": "⚠️ Пришлось подкупить тюремного геолога.", "currency_penalty": 300}
        ]
    },
    {
        "name": "Тюремный бунт",
        "attempt_text": "🚨 {user} устраивает тюремный бунт как отвлечение...",
        "success_text": "🚨 В хаосе бунта {user} незаметно сбегает! Свобода, наконец-то!",
        "fail_text": "🚨 Бунт быстро подавили. {user} был идентифицирован как подстрекатель и отправлен в одиночную камеру.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Другие заключённые присоединились к вашему делу! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Вы нашли ключ-карту охранника! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Вы разграбили комендатуру во время хаоса!", "currency_bonus": 300},
            {"text": "⭐️ Wi-Fi в тюрьме отключён - охрана отвлеклась! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Кто-то выпустил всех терапевтических собак! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Нашли тайное хранилище начальника тюрьмы!", "currency_bonus": 500},
            {"text": "⚠️ Охрана была готова! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Камеры видеонаблюдения поймали ваш план! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Вам пришлось подкупить другого заключённого, чтобы он молчал.", "currency_penalty": 250},
            {"text": "⚠️ Прибыл отряд спецназа! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Ваш лозунг бунта оказался слишком неуклюжим! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось заменить сломанную мебель.", "currency_penalty": 350}
        ]
    },
    {
        "name": "Маскировка под охрану",
        "attempt_text": "🕶 {user} надевает украденную форму охранника...",
        "success_text": "🕶 Никто не заподозрил {user}, когда тот спокойно вышел через главный вход! Идеальная маскировка!",
        "fail_text": "🕶 Форма оказалась из коллекции прошлого сезона. {user} сразу же заметили охранники, следящие за модой.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Смена смены создаёт путаницу! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Вы запомнили график патрулей охраны! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы нашли {currency} в кармане формы!", "currency_bonus": 250},
            {"text": "⭐️ Сегодня пятница - идеальное время! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Вы нашли секретный справочник приветствий охранников! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Обнаружены выигрыши охранника в покер!", "currency_bonus": 450},
            {"text": "⚠️ Ваши туфли не подходят к форме! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Один из охранников узнал вас! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Вам пришлось заплатить другому заключенному за форму.", "currency_penalty": 200},
            {"text": "⚠️ Ваш значок перевернут вверх ногами! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Вы забыли пароль охранника! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось купить настоящие ботинки охранника.", "currency_penalty": 275}
        ]   
    },
    {
        "name": "Побег в тележке с едой",
        "attempt_text": "🍽 {user} пытается спрятаться в кухонной тележке с доставкой еды...",
        "success_text": "🍽 Закопавшись под гору загадочного мяса, {user} был вывезен прямо в грузовик доставки. Мясо было ужасным, но свобода сладка!",
        "fail_text": "🍽 Возвращение отправителю! {user} забыл поставить достаточно марок на себя. У почтовой службы строгая политика в отношении отправки заключенных.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Сейчас праздничный сезон! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Вы нашли идеально подходящий ящик! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы обнаружили неотправленные денежные переводы на сумму {currency}!", "currency_bonus": 275},
            {"text": "⭐️ Визит санитарного инспектора - все отвлечены! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Повар находится в состоянии нервного срыва! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Найдены советы от кулинарного курса!", "currency_bonus": 350},
            {"text": "⚠️ Проверка посылок идет полным ходом! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Ящик слишком тяжелый! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось оплатить экспресс-доставку.", "currency_penalty": 225},
            {"text": "⚠️ Кто-то заказал неожиданную проверку! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Тележка пищит колесом! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось подкупить кухонный персонал.","currency_penalty": 300}
        ]
    },
    {
    "name": "Побег в прачечной",
    "attempt_text": "👕 {user} пытается выбраться вместе с грузовиком службы стирки грязного белья...",
    "success_text": "👕 Сложенный между свежими простынями, {user} наслаждался комфортной поездкой к свободе! Служба стирки тюрьмы с одно-звездочным рейтингом только что потеряла своего лучшего клиента.",
    "fail_text": "👕 {user} был обнаружен, когда не смог сдержать чихание. Оказалось, что прятаться в грязном белье - не лучшая идея.",
    "base_chance": 0.35,
    "events": [
           {"text": "⭐️ Белье сегодня особенно мягкое! (+15% шанс успеха)", "chance_bonus": 0.15},
           {"text": "⭐️ Сегодня особенно вонючий день - охранники не посмотрят! (+10% шанс успеха)", "chance_bonus": 0.10},
           {"text": "⭐️ Вы нашли ценности в мусоре!", "currency_bonus": 225},
           {"text": "⭐️ Статическое электричество делает вас невидимым! (+20% шанс успеха)", "chance_bonus": 0.20},
           {"text": "⭐️ Нашел счастливый носок! (+5% шанс успеха)", "chance_bonus": 0.05},
           {"text": "⭐️ Обнаружил деньги в сушилке!", "currency_bonus": 275},
           {"text": "⚠️ День проверки служебной собакой! (-15% шанс успеха)", "chance_penalty": 0.15},
           {"text": "⚠️ Контейнер имеет дыры! (-10% шанс успеха)", "chance_penalty": 0.10},
           {"text": "⚠️ Пришлось купить освежители воздуха.", "currency_penalty": 175},
           {"text": "⚠️ Стиральная машина протекает! (-15% шанс успеха)", "chance_penalty": 0.15},
           {"text": "⚠️ У вас аллергия на стиральный порошок средство! (-10% шанс успеха)", "chance_penalty": 0.10},
           {"text": "⚠️ Пришлось заплатить за премиальный смягчитель ткани.", "currency_penalty": 225}
        ]
    },
    {
    "name": "Замена посетителя",
    "attempt_text": "🎭 {user} пытается поменяться местами с посетителем...",
    "success_text": "🎭 Идеальное преступление! Двойной кузен {user} вошел, а {user} вышел. Семейные встречи будут неловкими.",
    "fail_text": "🎭 Оказывается, ваш 'идентичный' кузен был вашей полной противоположностью. Охранники не могли перестать смеяться, когда тащили вас обратно.",
    "base_chance": 0.35,
    "events": [
           {"text": "⭐️ Ваш кузен - мастер маскировки! (+20% шанс успеха)", "chance_bonus": 0.20},
           {"text": "⭐️ Комната для посетителей особенно многолюдна! (+10% шанс успеха)", "chance_bonus": 0.10},
           {"text": "⭐️ Ваш кузен дал вам немного денег!", "currency_bonus": 300},
           {"text": "⭐️ Сегодня день близнецов в тюрьме! (+25% шанс успеха)", "chance_bonus": 0.25},
           {"text": "⭐️ Ваши навыки макияжа улучшились! (+10% шанс успеха)", "chance_bonus": 0.10},
           {"text": "⭐️ Нашел деньги в шкафчике посетителя!", "currency_bonus": 400},
           {"text": "⚠️ Охранник проводит двойную проверку удостоверений личности! (-20% шанс успеха)", "chance_penalty": 0.20},
           {"text": "⚠️ У вашего кузена характерная походка! (-15% шанс успеха)", "chance_penalty": 0.15},
           {"text": "⚠️ Пришлось купить подходящую одежду.", "currency_penalty": 250},
           {"text": "⚠️ Установлены новые биометрические сканеры! (-25% шанс успеха)", "chance_penalty": 0.25},
           {"text": "⚠️ Вы забыли предысторию посетителя! (-15% шанс успеха)", "chance_penalty": 0.15},
           {"text": "⚠️ Пришлось купить косметику премиум-класса для маскировки.", "currency_penalty": 350}
        ]
    },
    {
        "name": "Спасение вертолетом",
        "attempt_text": "🚁 {user} сигнализирует своему сообщнику на вертолете...",
        "success_text": "🚁 В стиле боевика! {user} схватил веревочную лестницу и умчался прочь, пока охранники стояли в изумлении. Кажется, кто-то смотрел слишком много фильмов!",
        "fail_text": "🚁 Кульминация сюжета: оказалось, что это полицейский вертолет. {user} только что появился в 'Самых неловких побегах из тюрьмы мира'.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Ваш пилот - бывший дублер-каскадер! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Идеальные погодные условия! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Вы схватили коробку с мелкими деньгами тюрьмы!", "currency_bonus": 400},
            { "text": "⭐️ Охранники смотрят авиашоу! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Ваш пилот имеет опыт работы в играх! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Нашел экстренный фонд начальника тюрьмы!", "currency_bonus": 600},
            {"text": "⚠️ Активирована противосамолетная подсветка! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Сегодня сильный ветер! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Пришлось оплатить расходы пилота на топливо.", "currency_penalty": 200},
            {"text": "⚠️ Тюрьма установила противовоздушную оборону! (-30% шанс успеха)", "chance_penalty": 0.30},
            {"text": "⚠️ Наступила морская болезнь! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось оплатить техническое обслуживание вертолета.", "currency_penalty": 450}
        ]
    },
    {
        "name": "Побег через драматический кружок",
        "attempt_text": "🎭 {user} использует представление драматического кружка в качестве прикрытия...",
        "success_text": "🎭 Оскароносная игра! {user} сыграл свою роль настолько хорошо, что убедил всех, что он всего лишь актер, играющий заключенного. Отзывы были великолепными!",
        "fail_text": "🎭 {user} забыл свои реплики и импровизировал настоящий побег. Зрители подумали, что это часть шоу, и устроили стоячую овацию, когда его вытащили со сцены.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Вы снимаетесь в фильме 'Великий побег'! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Аудитория полностью увлечена! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы нашли деньги в коробке реквизита!", "currency_bonus": 250},
            {"text": "⭐️ Разведчик Бродвея в аудитории! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Свет прожекторов неисправен! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Выиграли приз конкурса драмы!", "currency_bonus": 450},
            {"text": "⚠️ Охранник является театральным критиком! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Страх сцены наступает! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось подкупить менеджера сцены.", "currency_penalty": 200},
            {"text": "⚠️ Метод актера-охранника дежурит! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Вы в неправильном костюме! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось заплатить за высококачественный реквизит.", "currency_penalty": 300}
        ]
    },
    {
    "name": "Путаница в почтовом отделении",
    "attempt_text": "📦 {user} пытается отправить себя почтой на свободу...",
    "success_text": "📦 Специальная доставка! {user} успешно отправили себя на свободу с премиальной доставкой. Однозвездочный отзыв за 'некомфортную упаковку' стоил того!",
    "fail_text": "📦 Возврат отправителю! {user} забыл наклеить достаточное количество марок на себя. У почтовой службы есть строгие правила относительно отправки заключенных.",
    "base_chance": 0.35,
    "events": [
            {"text": "⭐️ Сейчас предпраздничный сезон! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Вы нашли идеальную коробку! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы обнаружили неотправленные денежные переводы на сумму {currency}!", "currency_bonus": 275},
            {"text": "⭐️ Новый временный работник не проверяет этикетки! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Нашли пузырчатую пленку, чтобы спрятаться! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Обнаружили неправильно размещенную посылку Amazon!", "currency_bonus": 350},
            {"text": "⚠️ Проверка пакетов идет полным ходом! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Коробка слишком тяжелая! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось оплатить срочную доставку.", "currency_penalty": 225},
            {"text": "⚠️ Рентгеновский аппарат только что обновлен! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Вы не имеете права на премиальную доставку! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось оплатить ночную доставку.", "currency_penalty": 400}
        ]
    },
    {
    "name": "Гамбит с мусорным контейнером",
    "attempt_text": "🗑 {user} пытается спрятаться в мусоре...",
    "success_text": "🗑 Мусор одного человека - билет на свободу для другого! {user} выбрался наружу, пахнув гнилой рыбой, но хотя бы он свободен!",
    "fail_text": "🗑 {user} был найден, когда не мог сдержать чихание. Оказалось, что прятаться в старом мусоре - не самая лучшая идея.",
    "base_chance": 0.35,
    "events": [
            {"text": "⭐️ Водитель мусоровоза дремлет! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Сегодня особенно вонючий день - охранники не будут проверять мусор! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы нашли ценные вещи в мусоре!", "currency_bonus": 225},
            {"text": "⭐️ Это день осведомленности о переработке отходов! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Нашли защитный костюм в мусоре! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Обнаружили тайные сбережения уборщика!", "currency_bonus": 375},
            {"text": "⚠️ День инспекции служебной собаки! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Контейнер имеет дыры! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось купить освежители воздуха.", "currency_penalty": 175},
            {"text": "⚠️ Новые протоколы управления отходами! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Прессовочная установка неисправна! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Пришлось подкупить сборщика мусора.", "currency_penalty": 325}
        ]
    },
    {
    "name": "Побег группы тюремной музыки",
    "attempt_text": "🎸 {user} прячется внутри басового барабана тюремной группы...",
    "success_text": "🎸 {user} прокатился на ритме прямиком к свободе! Финальное выступление группы подозрительно облегчилось.",
    "fail_text": "🎸 {user} испортил большое финальное выступление, чихнув во время соло на барабанах. Критики остались недовольны.",
    "base_chance": 0.35,
    "events": [
            {"text": "⭐️ Группа играет особенно громко! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Вы находитесь в заднем ряду! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Вы нашли {currency} после выступления!", "currency_bonus": 200},
            {"text": "⭐️ Известный музыкант посещает сегодня! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Акустика идеальна! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Нашли банку для чаевых группы!", "currency_bonus": 325},
            {"text": "⚠️ Барабан имеет отверстие! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Охранник просит песню! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось подкупить барабанщика.", "currency_penalty": 175},
            {"text": "⚠️ Начальник тюрьмы - музыкальный критик! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Вы испытываете трудности с ритмом! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось заплатить за ремонт инструментов.", "currency_penalty": 275}
        ]
    },
    {
        "name": "Олимпийские игры в тюрьме",
        "attempt_text": "🏃 {user} участвует в ежегодных спортивных соревнованиях в тюрьме...",
        "success_text": "🏃 {user} взял золото в забеге на 100 метров... прямо мимо ворот! Рекордное выступление!",
        "fail_text": "🏃 {user} был дисквалифицирован за бег в неправильном направлении. Судьи остались недовольны.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Вы в отличной форме! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ Толпа болеет за вас! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Вы выиграли приз в размере {currency}!", "currency_bonus": 350},
            {"text": "⭐️ Олимпийский разведчик присутствует! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Энергетические закуски! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Нашли деньги из пула ставок!", "currency_bonus": 500},
            {"text": "⚠️ Профессиональный судья наблюдает! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Вы потянули мышцу! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Входной взнос и стоимость оборудования.", "currency_penalty": 275},
            {"text": "⚠️ Тестирование на наркотики в процессе! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Забыл растянуться! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось купить кроссовки премиум-класса.", "currency_penalty": 350}
        ]
    },
    {
        "name": "Художественная выставка в тюрьме",
        "attempt_text": "🎨 {user} планирует сбежать во время художественной выставки в тюрьме...",
        "success_text": "🎨 {user} притворился современной инсталляцией искусства и был отправлен в музей! Критики назвали это 'подвижным произведением о свободе'.",
        "fail_text": "🎨 Поза 'Статуи Свободы' {user} оказалась недостаточно убедительной. Художественные критики дали ей нулевые звезды.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Ваше искусство заняло первое место! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Галерея заполнена людьми! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Кто-то купил ваше произведение искусства!", "currency_bonus": 275},
            {"text": "⭐️ Знаменитый коллекционер произведений искусства посещает выставку! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Выставка абстрактного искусства - идеальное прикрытие! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Выиграл премию зрительских симпатий!", "currency_bonus": 450},
            {"text": "⚠️ Куратор подозревает что-то неладное! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Краска еще влажная! (-10% шанс успеха)", "chance_penalty": 0.10},
            {"text": "⚠️ Пришлось купить художественные принадлежности.", "currency_penalty": 225},
            {"text": "⚠️ На месте аутентификатор искусства! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Ваше шедевр смазано! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось купить дорогие художественные материалы.", "currency_penalty": 375}
        ]
    },
    {
        "name": "Кулинарное шоу в тюрьме",
        "attempt_text": "👨‍🍳 {user} принимает участие в кулинарном конкурсе в тюрьме...",
        "success_text": "👨‍🍳 Суфле {user} было настолько хорошим, что его немедленно взяли на работу в ресторан с пятью звездами... снаружи!",
        "fail_text": "👨‍🍳 План побега {user} провалился, как и его неудавшееся суфле. Вернитесь к обязанностям на кухне.",
        "base_chance": 0.35,
        "events": [
            {"text": "⭐️ Ваше блюдо впечатлило Гордона Рамзи! (+20% шанс успеха)", "chance_bonus": 0.20},
            {"text": "⭐️ На кухне царит хаос! (+15% шанс успеха)", "chance_bonus": 0.15},
            {"text": "⭐️ Выиграл приз в размере {currency}!", "currency_bonus": 300},
            {"text": "⭐️ Знаменитый шеф-повар приглашен в качестве судьи! (+25% шанс успеха)", "chance_bonus": 0.25},
            {"text": "⭐️ Нашли секретную книгу рецептов! (+10% шанс успеха)", "chance_bonus": 0.10},
            {"text": "⭐️ Возможность заключения контракта на кейтеринг!", "currency_bonus": 550},
            {"text": "⚠️ Кулинарный критик следит за вами! (-20% шанс успеха)", "chance_penalty": 0.20},
            {"text": "⚠️ Сигнал пожарной тревоги на кухне! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось купить ингредиенты премиум-класса.", "currency_penalty": 250},
            {"text": "⚠️ Неожиданный визит санитарного инспектора! (-25% шанс успеха)", "chance_penalty": 0.25},
            {"text": "⚠️ Ваш соус слишком пресный! (-15% шанс успеха)", "chance_penalty": 0.15},
            {"text": "⚠️ Пришлось купить трюфельные ингредиенты.", "currency_penalty": 400}
        ]
    }
]
        
 
