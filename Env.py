from pymongo import MongoClient

from chess import uci

from modules.fishnet.fishnet import stockfish_command

from modules.core.Game import GameDB
from modules.core.GameAnalysis import GameAnalysisDB
from modules.core.Player import PlayerDB

from modules.Api import Api

from modules.irwin.Irwin import Irwin
from modules.irwin.TrainingStats import TrainingStatsDB
from modules.irwin.FalseReports import FalseReportsDB
from modules.irwin.GameAnalysisPlayerPivot import GameAnalysisPlayerPivotDB
from modules.irwin.ConfidentGameAnalysisPivot import ConfidentGameAnalysisPivotDB
from modules.irwin.PlayerGameActivations import PlayerGameActivationsDB
from modules.irwin.PlayerGameWords import PlayerGameWordsDB

class Env:
  def __init__(self, settings):
    self.settings = settings

    self.engine = uci.popen_engine(stockfish_command(settings['stockfish']['update']))
    self.engine.setoption({'Threads': settings['stockfish']['threads'], 'Hash': settings['stockfish']['memory']})
    self.engine.uci()
    self.infoHandler = uci.InfoHandler()
    self.engine.info_handlers.append(self.infoHandler)

    self.api = Api(settings['api']['url'], settings['api']['token'])

    # Set up mongodb
    self.client = MongoClient(settings['db']['host'])
    self.db = self.client.irwin
    if settings['db']['authenticate']:
      self.db.authenticate(
        settings['db']['authentication']['username'],
        settings['db']['authentication']['password'], mechanism='MONGODB-CR')

    # Colls
    self.playerColl = self.db.player
    self.gameColl = self.db.game
    self.gameAnalysisColl = self.db.gameAnalysis

    self.gameAnalysisPlayerPivotColl = self.db.gameAnalysisPlayerPivot
    self.confidentGameAnalysisPivotColl = self.db.confidentGameAnalysisPivot
    self.playerGameActivationsColl = self.db.playerGameActivations
    self.playerGameWordsColl = self.db.playerGameWords

    # database abstraction
    self.playerDB = PlayerDB(self.playerColl)
    self.gameDB = GameDB(self.gameColl)
    self.gameAnalysisDB = GameAnalysisDB(self.gameAnalysisColl)

    self.gameAnalysisPlayerPivotDB = GameAnalysisPlayerPivotDB(self.gameAnalysisPlayerPivotColl)
    self.confidentGameAnalysisPivotDB = ConfidentGameAnalysisPivotDB(self.confidentGameAnalysisPivotColl)
    self.playerGameActivationsDB = PlayerGameActivationsDB(self.playerGameActivationsColl)
    self.playerGameWordsDB = PlayerGameWordsDB(self.playerGameWordsColl)

    # Irwin
    self.irwin = Irwin(self, settings['irwin'])

  def restartEngine(self):
    self.engine.kill()
    self.engine = uci.popen_engine(stockfish_command(self.settings['stockfish']['update']))
    self.engine.setoption({'Threads': self.settings['stockfish']['threads'], 'Hash': self.settings['stockfish']['memory']})
    self.engine.uci()
    self.infoHandler = uci.InfoHandler()
    self.engine.info_handlers.append(self.infoHandler)

  def __del__(self):
    print("Removing Env")
    self.engine.kill()
    try:
      del self.irwin
    except TypeError:
      pass