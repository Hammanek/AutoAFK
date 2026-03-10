"""Dailies Runner - Executes all daily activities in correct order"""
from typing import Optional
import logging
import os
import time

from src.core.activity_manager import ActivityManager

logger = logging.getLogger(__name__)


def execute_dailies(activity_manager: ActivityManager, 
                   pause_event=None, 
                   stop_event=None) -> None:
    """
    Execute all daily activities in the correct order
    
    This function runs all configured daily activities following the exact
    order from the original version for compatibility.
    
    Args:
        activity_manager: ActivityManager instance with all activity modules
        pause_event: Optional threading.Event for pausing execution
        stop_event: Optional threading.Event for stopping execution
    """
    config = activity_manager.config
    device_manager = activity_manager.device_manager
    game_controller = activity_manager.game_controller
    notification_manager = activity_manager.notification_manager
    
    # Expand menus and wait for game
    game_controller.expand_menus()
    game_controller.wait_until_game_active()
    
    logger.info("Device connected, running dailies...")

    # Run dailies in EXACT order as old version for compatibility
    # Order is critical - DO NOT CHANGE without testing!
    
    # 1. Collect AFK Rewards
    if config.getboolean('DAILIES', 'collectRewards', fallback=True):
        activity_manager.daily.collect_afk_rewards()
        device_manager.tap(20, 20)  # Clear popups
        
    # 2. Collect Mail
    if config.getboolean('DAILIES', 'collectMail', fallback=True):
        activity_manager.daily.collect_mail()
        device_manager.tap(20, 20)
        
    # 3. Send/Receive Companion Points (with optional merc lending)
    if config.getboolean('DAILIES', 'companionPoints', fallback=True):
        lend_mercs = config.getboolean('DAILIES', 'lendMercs', fallback=False)
        activity_manager.daily.collect_companion_points(lend_mercs)
        device_manager.tap(20, 20)
        
    # 4. Fast Rewards
    fast_rewards = config.getint('DAILIES', 'fastrewards', fallback=0)
    if fast_rewards > 0:
        activity_manager.daily.collect_fast_rewards(fast_rewards)
        device_manager.tap(20, 20)
        
    # 5. Attempt Campaign
    if config.getboolean('DAILIES', 'attemptCampaign', fallback=False):
        activity_manager.daily.attempt_campaign()
        device_manager.tap(20, 20)
        
    # 6. Handle Bounties (solo, team, event)
    if (config.getboolean('BOUNTIES', 'dispatchSoloBounties', fallback=False) or 
        config.getboolean('BOUNTIES', 'dispatchTeamBounties', fallback=False) or
        config.getboolean('BOUNTIES', 'dispatchEventBounties', fallback=False)):
        activity_manager.bounty.handle_bounties()
        device_manager.tap(20, 20)
        
    # 7. Arena of Heroes
    if config.getboolean('ARENA', 'battleArena', fallback=False):
        battles = config.getint('ARENA', 'arenaBattles', fallback=5)
        opponent = config.getint('ARENA', 'arenaOpponent', fallback=1)
        activity_manager.arena.battle_arena_of_heroes(battles, opponent, pause_event, stop_event)
        device_manager.tap(20, 20)
        
    # 8. Collect Treasure Scramble Rewards
    if config.getboolean('ARENA', 'tsCollect', fallback=False):
        activity_manager.arena.collect_treasure_scramble()
        device_manager.tap(20, 20)
        
    # 9. Collect Gladiator Coins
    if config.getboolean('ARENA', 'gladiatorCollect', fallback=False):
        activity_manager.arena.collect_gladiator_coins()
        device_manager.tap(20, 20)
        
    # 10. Collect Fountain of Time
    if config.getboolean('DAILIES', 'fountainOfTime', fallback=False):
        activity_manager.daily.collect_fountain_of_time()
        device_manager.tap(20, 20)
        
    # 11. Handle King's Tower
    if config.getboolean('DAILIES', 'kingsTower', fallback=False):
        activity_manager.tower.handle_kings_tower()
        device_manager.tap(20, 20)
        
    # 12. Collect Inn Gifts
    if config.getboolean('DAILIES', 'collectInn', fallback=False):
        activity_manager.daily.collect_inn_gifts()
        device_manager.tap(20, 20)
        
    # 13. Guild Hunts
    if config.getboolean('DAILIES', 'guildHunt', fallback=False):
        activity_manager.guild.handle_guild_hunts()
        device_manager.tap(20, 20)
        
    # 14. Store Purchases
    shop_refreshes = config.getint('DAILIES', 'shoprefreshes', fallback=0)
    if config.getboolean('DAILIES', 'storePurchases', fallback=False):
        activity_manager.shop.shop_purchases(shop_refreshes)
        device_manager.tap(20, 20)
        
    # 15. Twisted Realm
    if config.getboolean('DAILIES', 'twistedRealm', fallback=False):
        activity_manager.tower.handle_twisted_realm()
        device_manager.tap(20, 20)
        
    # 16. Fight of Fates
    if config.getboolean('EVENTS', 'fightOfFates', fallback=False):
        battles = config.getint('EVENTS', 'fofBattles', fallback=3)
        activity_manager.misc.handle_fight_of_fates(battles)
        device_manager.tap(20, 20)
        
    # 17. Battle of Blood
    if config.getboolean('EVENTS', 'battleOfBlood', fallback=False):
        battles = config.getint('EVENTS', 'bobBattles', fallback=3)
        activity_manager.misc.handle_battle_of_blood(battles)
        device_manager.tap(20, 20)
        
    # 18. Circus Tour
    if config.getboolean('EVENTS', 'circusTour', fallback=False):
        battles = config.getint('EVENTS', 'circusBattles', fallback=3)
        activity_manager.misc.handle_circus_tour(battles)
        device_manager.tap(20, 20)
        
    # 19. Run Labyrinth
    if config.getboolean('DAILIES', 'runLab', fallback=False):
        activity_manager.labyrinth.handle_labyrinth()
        device_manager.tap(20, 20)
        
    # 20. Heroes of Esperia
    if config.getboolean('EVENTS', 'heroesOfEsperia', fallback=False):
        count = config.getint('EVENTS', 'hoeBattles', fallback=3)
        opponent = config.getint('EVENTS', 'hoeOpponent', fallback=4)
        activity_manager.misc.handle_heroes_of_esperia(count, opponent)
        device_manager.tap(20, 20)
        
    # 21. Summon Hero (single scroll)
    if config.getboolean('DAILIES', 'summonHero', fallback=False):
        activity_manager.summon.summon_hero_scroll()
        device_manager.tap(20, 20)
        
    # 22. Collect Daily/Weekly Quests
    if config.getboolean('DAILIES', 'collectQuests', fallback=False):
        activity_manager.daily.collect_quests()
        device_manager.tap(20, 20)
        
    # 23. Collect Merchant Deals/Nobles
    if config.getboolean('DAILIES', 'collectMerchants', fallback=False):
        activity_manager.shop.clear_merchant()
        device_manager.tap(20, 20)
        
    # 24. Use Bag Consumables
    if config.getboolean('DAILIES', 'useBagConsumables', fallback=False):
        activity_manager.daily.use_bag_consumables()
        device_manager.tap(20, 20)
        
    # 25. Auto Level Up
    if config.getboolean('DAILIES', 'levelUp', fallback=False):
        activity_manager.daily.level_up_heroes()
        device_manager.tap(20, 20)
        
    # 26. Get Mercenaries (custom code)
    if config.getboolean('ADVANCED', 'customCode', fallback=False):
        activity_manager.summon.get_mercenaries()
        device_manager.tap(20, 20)
        
    # Desktop notification
    if notification_manager:
        notification_manager.send_notification("Dailies Complete", "All daily activities finished!")
    
    # Optional: Hibernate system when done
    if config.getboolean('DAILIES', 'hibernate', fallback=False):
        logger.warning("Hibernating system in 1 minute...")
        time.sleep(60)
        os.system("shutdown /h")
    
    logger.info("Dailies completed successfully!")
