# import yfinance as yf
# import pandas as pd
# from sqlalchemy import create_engine, Column, Integer, String, MetaData
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST ,DATABASE_NAME

# # Database configuration
# DATABASE_URL = f'mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# Base = declarative_base()

# # Define Trade_Symbols table schema
# class TradeSymbol(Base):
#     __tablename__ = 'base_tradesymbols'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String(10), nullable=False)
#     type = Column(String(10), nullable=False)
#     description = Column(String(255), nullable=True)
#     exchange = Column(String(50), nullable=True)
#     company_name = Column(String(255), nullable=True)
#     sector = Column(String(100), nullable=True)
#     industry = Column(String(100), nullable=True)

# Base.metadata.create_all(engine)

# # # Get data for a list of symbols
# # def get_sp500_symbols():
# #     url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
# #     sp500_table = pd.read_html(url, header=0)[0]
# #     symbols = sp500_table['Symbol'].tolist()
# #     return symbols

# # # Function to get NASDAQ symbols
# # def get_nasdaq_symbols():
# #     url = "https://en.wikipedia.org/wiki/NASDAQ-100"
# #     tables = pd.read_html(url, header=0)
# #     nasdaq_table = tables[4]
# #     nasdaq_table.columns = nasdaq_table.columns.str.strip()

# #     if 'Ticker' in nasdaq_table.columns:
# #         symbols = nasdaq_table['Ticker'].tolist()
# #     elif 'Symbol' in nasdaq_table.columns:
# #         symbols = nasdaq_table['Symbol'].tolist()
# #     else:
# #         raise KeyError("Couldn't find the 'Ticker' or 'Symbol' column in the NASDAQ table.")

# #     return symbols

# # etf_symbols = [
# #     'SQQQ', 'SPY', 'SOXL', 'TQQQ', 'XLF', 'TLT', 'FXI', 'QQQ', 'HYG', 'SLV',
# #     'SPXS', 'TSLL', 'IBIT', 'IWM', 'EEM', 'SOXS', 'GDX', 'LQD', 'EWZ', 'TZA',
# #     'SH', 'KWEB', 'NVDL', 'MSOS', 'ARKK', 'VEA', 'DUST', 'XBI', 'BITO', 'IEMG',
# #     'BOIL', 'VWO', 'XLI', 'GLD', 'AGG', 'IJH', 'TMF', 'GOVT', 'IYR', 'RSP',
# #     'EMB', 'QID', 'YANG', 'XLK', 'BITX', 'INDA', 'VOO', 'UPRO', 'IVV', 'SPXL',
# #     'PSLV', 'VIXY', 'XLC', 'ASHR'
# # ]

# # # Get S&P 500 symbols
# # sp500_symbols = get_sp500_symbols()
# # print(f"Total S&P 500 symbols fetched: {len(sp500_symbols)}")

# # # Get NASDAQ symbols
# # nasdaq_symbols = get_nasdaq_symbols()
# # print(f"Total NASDAQ symbols fetched: {len(nasdaq_symbols)}")

# # # Combine S&P 500 and NASDAQ symbols
# # all_symbols = sp500_symbols + nasdaq_symbols + etf_symbols
# # print(f"Total combined symbols fetched: {len(all_symbols)}")

# # def get_symbols_from_csv():
# #             df = pd.read_csv('stock_symbols.csv')
# #             symbols = df['Symbol'].tolist()
# #             return symbols

# # all_symbols=get_symbols_from_csv()


# # Download data
# data = yf.download(all_symbols, start='2022-01-01', auto_adjust=True, group_by='ticker')

# # Function to get company details
# def get_company_details(symbol):
#     try:
#         stock = yf.Ticker(symbol)
#         info = stock.info
#         return info.get('exchange', ''), info.get('shortName', ''), info.get('sector', ''), info.get('industry', ''), info.get('quoteType', 'Stock')
#     except Exception as e:
#         print(f"Error fetching data for {symbol}: {e}")
#         return '', '', '', '', 'Stock'

# # Insert data into the Trade_Symbols table
# session = Session()
# for symbol in all_symbols:
#     try:
#         if symbol in data and not data[symbol].empty:
#             exchange, company_name, sector, industry, asset_type = get_company_details(symbol)
#             type = 'Stock' if asset_type == 'EQUITY' else 'ETF'
#             description = ''
#             trade_symbol = TradeSymbol(
#                 symbol=symbol,
#                 type=type,
#                 description=description,
#                 exchange=exchange,
#                 company_name=company_name,
#                 sector=sector,
#                 industry=industry
#             )
#             session.merge(trade_symbol)
#         else:
#             print(f"No data for {symbol}")
#     except Exception as e:
#         print(f"Error processing {symbol}: {e}")

# # Commit the changes and close the session
# session.commit()
# session.close()
