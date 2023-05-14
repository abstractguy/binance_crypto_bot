//@version=5
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © Samuel Duclos

strategy('Custom Strategy', overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100, calc_on_order_fills=true)
max_bars_back = 1000

RenkoATRLength = input(25, title='Renko ATR Length')
CCILength = input(22, title='CCI Length')
MACDFastLength = input(12, title='MACD Fast Length')
MACDSlowLength = input(26, title='MACD Slow Length')
MACDLength = input(9, title='MACD SignalLength')
CHOPLength = input(14, title='Choppiness Length')
MFILength = input(11, title='MFI Length')
ADXLength = input(14, title='ADX Smoothing')
ADXTrigger = input(20, title='ADX Trigger')
DILength = input(8, title='DI Length')
BOLLLength = input(11, title='Middle Bollinger Band Length')

// Make input options that configure backtest date range.
startDate = input.int(title='Start Date', defval=1, minval=1, maxval=31)
startMonth = input.int(title='Start Month', defval=5, minval=1, maxval=12)
startYear = input.int(title='Start Year', defval=2022, minval=1800, maxval=2100)

endDate = input.int(title='End Date', defval=1, minval=1, maxval=31)
endMonth = input.int(title='End Month', defval=4, minval=1, maxval=12)
endYear = input.int(title='End Year', defval=2023, minval=1800, maxval=2100)

// Look if the close time of the current bar falls inside the date range.
inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)

open_1min = request.security(syminfo.tickerid, '1', open)
high_1min = request.security(syminfo.tickerid, '1', high)
low_1min = request.security(syminfo.tickerid, '1', low)
close_1min = request.security(syminfo.tickerid, '1', close)
volume_1min = request.security(syminfo.tickerid, '1', volume)

open_5min = request.security(syminfo.tickerid, '5', open)
high_5min = request.security(syminfo.tickerid, '5', high)
low_5min = request.security(syminfo.tickerid, '5', low)
close_5min = request.security(syminfo.tickerid, '5', close)
volume_5min = request.security(syminfo.tickerid, '5', volume)

open_15min = request.security(syminfo.tickerid, '15', open)
high_15min = request.security(syminfo.tickerid, '15', high)
low_15min = request.security(syminfo.tickerid, '15', low)
close_15min = request.security(syminfo.tickerid, '15', close)
volume_15min = request.security(syminfo.tickerid, '15', volume)

open_24min = request.security(syminfo.tickerid, '24', open)
high_24min = request.security(syminfo.tickerid, '24', high)
low_24min = request.security(syminfo.tickerid, '24', low)
close_24min = request.security(syminfo.tickerid, '24', close)
volume_24min = request.security(syminfo.tickerid, '24', volume)

indexHighTF = barstate.isrealtime ? 1 : 0
indexCurrTF = barstate.isrealtime ? 0 : 1
open_30min = request.security(syminfo.tickerid, '30', open[indexHighTF])[indexCurrTF]
high_30min = request.security(syminfo.tickerid, '30', high[indexHighTF])[indexCurrTF]
low_30min = request.security(syminfo.tickerid, '30', low[indexHighTF])[indexCurrTF]
close_30min = request.security(syminfo.tickerid, '30', close[indexHighTF])[indexCurrTF]
volume_30min = request.security(syminfo.tickerid, '30', volume[indexHighTF])[indexCurrTF]

open_1h = request.security(syminfo.tickerid, '60', open)
high_1h = request.security(syminfo.tickerid, '60', high)
low_1h = request.security(syminfo.tickerid, '60', low)
close_1h = request.security(syminfo.tickerid, '60', close)
volume_1h = request.security(syminfo.tickerid, '60', volume)

open_2h = request.security(syminfo.tickerid, '120', open)
high_2h = request.security(syminfo.tickerid, '120', high)
low_2h = request.security(syminfo.tickerid, '120', low)
close_2h = request.security(syminfo.tickerid, '120', close)
volume_2h = request.security(syminfo.tickerid, '120', volume)

open_4h = request.security(syminfo.tickerid, '240', open)
high_4h = request.security(syminfo.tickerid, '240', high)
low_4h = request.security(syminfo.tickerid, '240', low)
close_4h = request.security(syminfo.tickerid, '240', close)
volume_4h = request.security(syminfo.tickerid, '240', volume)

open_12h = request.security(syminfo.tickerid, '720', open)
high_12h = request.security(syminfo.tickerid, '720', high)
low_12h = request.security(syminfo.tickerid, '720', low)
close_12h = request.security(syminfo.tickerid, '720', close)
volume_12h = request.security(syminfo.tickerid, '720', volume)

open_1d = request.security(syminfo.tickerid, '1440', open)
high_1d = request.security(syminfo.tickerid, '1440', high)
low_1d = request.security(syminfo.tickerid, '1440', low)
close_1d = request.security(syminfo.tickerid, '1440', close)
volume_1d = request.security(syminfo.tickerid, '1440', volume)




heikin_ashi_1(open_, high_, low_, close_) =>
    ha_open_ = (open_ + close_) / 2
    ha_close = (open_ + high_ + low_ + close_) / 4
    ha_open = na(open_[1]) ? (open_ + close_) / 2 : (ha_open_[1] + ha_close[1]) / 2
    ha_high = high_
    ha_low = low_
    [ha_open, ha_high, ha_low, ha_close]

heikin_ashi2(open_, high_, low_, close_) =>
    [ha_open, ha_high, ha_low, ha_close] = heikin_ashi_1(open_, high_, low_, close_)
    [ha2_open, ha2_high, ha2_low, ha2_close] = heikin_ashi_1(ha_open, ha_high, ha_low, ha_close)
    [ha2_open, ha2_high, ha2_low, ha2_close]


//ha_open_1min = open_1min
//ha_high_1min = high_1min
//ha_low_1min = low_1min
//ha_close_1min = close_1min
//
//ha_open_5min = open_5min
//ha_high_5min = high_5min
//ha_low_5min = low_5min
//ha_close_5min = close_5min
//
//ha_open_15min = open_15min
//ha_high_15min = high_15min
//ha_low_15min = low_15min
//ha_close_15min = close_15min
//
//ha_open_30min = open_30min
//ha_high_30min = high_30min
//ha_low_30min = low_30min
//ha_close_30min = close_30min
//
//ha_open_1h = open_1h
//ha_high_1h = high_1h
//ha_low_1h = low_1h
//ha_close_1h = close_1h
//
//ha_open_1d = open_1d
//ha_high_1d = high_1d
//ha_low_1d = low_1d
//ha_close_1d = close_1d

[ha_open_1min, ha_high_1min, ha_low_1min, ha_close_1min] = heikin_ashi_1(open_1min, high_1min, low_1min, close_1min)
[ha_open_5min, ha_high_5min, ha_low_5min, ha_close_5min] = heikin_ashi_1(open_5min, high_5min, low_5min, close_5min)
[ha_open_15min, ha_high_15min, ha_low_15min, ha_close_15min] = heikin_ashi_1(open_15min, high_15min, low_15min, close_15min)
[ha_open_24min, ha_high_24min, ha_low_24min, ha_close_24min] = heikin_ashi_1(open_24min, high_24min, low_24min, close_24min)
[ha_open_30min, ha_high_30min, ha_low_30min, ha_close_30min] = heikin_ashi_1(open_30min, high_30min, low_30min, close_30min)
[ha_open_1h, ha_high_1h, ha_low_1h, ha_close_1h] = heikin_ashi_1(open_1h, high_1h, low_1h, close_1h)
[ha_open_2h, ha_high_2h, ha_low_2h, ha_close_2h] = heikin_ashi_1(open_2h, high_2h, low_2h, close_2h)
[ha_open_4h, ha_high_4h, ha_low_4h, ha_close_4h] = heikin_ashi_1(open_4h, high_4h, low_4h, close_4h)
[ha_open_12h, ha_high_12h, ha_low_12h, ha_close_12h] = heikin_ashi_1(open_12h, high_12h, low_12h, close_12h)
[ha_open_1d, ha_high_1d, ha_low_1d, ha_close_1d] = heikin_ashi_1(open_1d, high_1d, low_1d, close_1d)


renko_trigger(open_, high_, low_, close_) =>
    //hlc3_ = (ha_high_30min + ha_low_30min + ha_close_30min) / 3
    //hlc3_ = (high_30min + low_30min + close_30min) / 3
    hlc3_ = (high_ + low_ + close_) / 3
    renko_tickerid = ticker.renko(syminfo.tickerid, 'ATR', RenkoATRLength)
    renko_close = request.security(renko_tickerid, timeframe.period, hlc3_)
    //renko_close = request.security(renko_tickerid, timeframe.period, close_)
    //renko_close = request.security(renko_tickerid, timeframe.period, high_)
    //renko_close = request.security(renko_tickerid, timeframe.period, low_)
    renko_close > renko_close[1]



pine_mfi_1(high_, low_, close_, length) =>
    x = (high_ + low_ + close_) / 3
    currentMf = 0.0
    previousMf = 0.0
    positiveMf = 0.0
    negativeMf = 0.0
    for i = 0 to length - 1 by 1
        currentMf := x[i] * volume[i]
        previousMf := x[i + 1] * volume[i + 1]
        if na(x[i + 1])
            positiveMf := na
            negativeMf := na
            negativeMf
        else
            if x[i] > x[i + 1]
                positiveMf += currentMf
                positiveMf

            if x[i] < x[i + 1]
                negativeMf += currentMf
                negativeMf

    ratio = positiveMf / negativeMf
    mfi = 100 - 100 / (1 + ratio)
    mfi

pine_mfi_2(high_, low_, close_, length) =>
    x = (high_ + low_ + close_) / 3
    currentMf = 0.0
    previousMf = 0.0
    positiveMf = 0.0
    negativeMf = 0.0
    for i = 0 to length - 1 by 1
        currentMf := x[i] * volume[i]
        previousMf := x[i + 1] * volume[i + 1]
        if na(x[i + 1])
            positiveMf := na
            negativeMf := na
            negativeMf
        else
            if x[i] > x[i + 1]
                positiveMf += currentMf
                positiveMf

            if x[i] < x[i + 1]
                negativeMf += currentMf
                negativeMf

    ratio = positiveMf / negativeMf
    mfi = 100 - 100 / (1 + ratio)
    mfi

pine_tr_1(high_, low_, close_) =>
    na(high_[1]) ? high_ - low_ : math.max(math.max(high_ - low_, math.abs(high_ - close_[1])), math.abs(low_ - close_[1]))

pine_atr_1(high_, low_, close_, length) =>
    trueRange = pine_tr_1(high_, low_, close_)
    ta.rma(trueRange, length)

dirmov(high_, low_, close_, len) =>
    up = ta.change(high_)
    down = -ta.change(low_)
    truerange = pine_atr_1(high_, low_, close_, len)
    plus = fixnan(100 * ta.rma(up > down and up > 0 ? up : 0, len) / truerange)
    minus = fixnan(100 * ta.rma(down > up and down > 0 ? down : 0, len) / truerange)
    [plus, minus]

adx(high_, low_, close_, DILength, ADXLength) =>
    [plus, minus] = dirmov(high_, low_, close_, DILength)
    sum = plus + minus
    adx = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), ADXLength)
    [adx, plus, minus]

adx_trigger(high_, low_, close_) =>
    [sig, up, down] = adx(high_, low_, close_, DILength, ADXLength)
    //(up > down)
    up > down and sig > ADXTrigger

pine_eom(high_, low_, volume_) =>
    cumVol = 0.
    cumVol += nz(volume_)
    ta.sma(10000 * ta.change((high_ + low_) / 2) * (high_ - low_) / volume_, 14)

eom_trigger(high_, low_, volume_) =>
    ind = pine_eom(high_, low_, volume_)
    ta.change(ind) > 0

cci_trigger(high_, low_, close_) =>
    ind = ta.cci(close_, CCILength)
    MFI = pine_mfi_1(high_, low_, close_, MFILength)
    //(ind > 0)
    ind[1] < 0 and ind > 0
    //((ind > 0) or ((MFI > 20)))

cci_entry_trigger(high_, low_, close_) =>
    ind = ta.cci(close_, CCILength)
    MFI = pine_mfi_2(high_, low_, close_, MFILength)
    //(ind > 0)
    ind[1] < 0 and ind > 0
    //((ind > 0) or ((MFI > 20)))

positive_macd_trigger(close_) =>
    [macdLine, signalLine, histLine] = ta.macd(close_, MACDFastLength, MACDSlowLength, MACDLength)
    histLine > histLine[1] or macdLine > signalLine

negative_macd_trigger(close_) =>
    [macdLine, signalLine, histLine] = ta.macd(close_, MACDFastLength, MACDSlowLength, MACDLength)
    histLine < histLine[1] and macdLine < signalLine

choppiness(high_, low_, close_, CHOPLength) =>
    100 * math.log10(math.sum(pine_atr_1(high_, low_, close_, 1), CHOPLength) / (ta.highest(high_, CHOPLength) - ta.lowest(low_, CHOPLength))) / math.log10(CHOPLength)

choppiness_trigger(high_, low_, close_) =>
    //choppiness(high_, low_, close_, CHOPLength) < 38.2
    choppiness(high_, low_, close_, CHOPLength) < 61.8

bollinger_band_middle_band(close_, BOLLLength) =>
    ta.sma(close_, BOLLLength)

bollinger_band_trigger(close_) =>
    middle_band = bollinger_band_middle_band(close_, BOLLLength)
    close_ > middle_band


//condADXLong = adx_trigger(ha_high_1min, ha_low_1min, ha_close_1min, DILength, ADXLength)
//condADXShort = (not condADXLong)
//
//condEOMLong = eom_trigger(ha_high_1min, ha_low_1min, volume)
//condEOMShort = (not condEOMLong)
//
//condCCILong = cci_trigger(ha_close_1min, CCILength)
//condCCIShort = (not condCCILong)
//
//condMACDLong = macd_trigger(close_)
//condMACDShort = (not condMACDLong)

entry_trigger_1min(open_, high_, low_, close_) =>
    condCCILong = cci_trigger(high_, low_, close_)
    condADXLong = adx_trigger(high_, low_, close_)
    //condMACDLong = positive_macd_trigger(close_)
    //condBBandLong = bollinger_band_trigger(close_)
    //condCHOPLong = choppiness_trigger(high_, low_, close_)
    //((condCCILong or condADXLong) and condMACDLong and condBBandLong)
    //condRenkoLong = renko_trigger(open_, high_, low_, close_)
    //((condCCILong or condADXLong) and condMACDLong)
    //((condCCILong or condADXLong) and condRenkoLong)
    //(condRenkoLong)
    //(close_ > high_[1])
    //(close_ > open_)
    //(condCCILong or condADXLong)
    condCCILong

positive_timed_trigger_1min(open_, high_, low_, close_) =>
    condTriggerLong = entry_trigger_1min(open_, high_, low_, close_)
    condMACDLong = positive_macd_trigger(close_)
    //(condTriggerLong and condMACDLong)
    condTriggerLong

negative_timed_trigger_1min(open_, high_, low_, close_) =>
    condTriggerShort = not entry_trigger_1min(open_, high_, low_, close_)
    condMACDShort = negative_macd_trigger(close_)
    //((not condTriggerShort) and condMACDShort)
    condTriggerShort

entry_trigger(open_, high_, low_, close_) =>
    condCCILong = cci_trigger(high_, low_, close_)
    condADXLong = adx_trigger(high_, low_, close_)
    //condMACDLong = macd_trigger(close_)
    //condBBandLong = bollinger_band_trigger(close_)
    //condCHOPLong = choppiness_trigger(high_, low_, close_)
    //((condCCILong or condADXLong) and condMACDLong and condBBandLong)
    condRenkoLong = renko_trigger(open_, high_, low_, close_)
    //(condCCILong or condADXLong)
    //((condCCILong or condADXLong) and condRenkoLong)
    condRenkoLong

positive_timed_trigger(open_, high_, low_, close_) =>
    condTriggerLong = entry_trigger(open_, high_, low_, close_)
    condMACDLong = positive_macd_trigger(close_)
    //(condTriggerLong and condMACDLong)
    condTriggerLong

negative_timed_trigger(open_, high_, low_, close_) =>
    condTriggerShort = not entry_trigger(open_, high_, low_, close_)
    condMACDShort = negative_macd_trigger(close_)
    //((not condTriggerShort) and condMACDShort)
    condTriggerShort


//condLong = timed_trigger(ha_high_1min, ha_low_1min, ha_close_1min)
//condShort = (not condLong)

condLong1min = positive_timed_trigger_1min(ha_open_1min, ha_high_1min, ha_low_1min, ha_close_1min)
//condLong1min = positive_timed_trigger_1min(open_1min, high_1min, low_1min, close_1min)
condLong5min = positive_timed_trigger_1min(ha_open_5min, ha_high_5min, ha_low_5min, ha_close_5min)
condLong15min = positive_timed_trigger_1min(ha_open_15min, ha_high_15min, ha_low_15min, ha_close_15min)
condLong24min = positive_timed_trigger(ha_open_24min, ha_high_24min, ha_low_24min, ha_close_24min)
//condLong30min = positive_timed_trigger(ha_open_30min, ha_high_30min, ha_low_30min, ha_close_30min)
condLong30min = positive_timed_trigger(open_30min, high_30min, low_30min, close_30min)
condLong30min_cci = positive_timed_trigger_1min(ha_open_30min, ha_high_30min, ha_low_30min, ha_close_30min)
condLong1h = positive_timed_trigger(ha_open_1h, ha_high_1h, ha_low_1h, ha_close_1h)
condLong1h_cci = positive_timed_trigger_1min(ha_open_1h, ha_high_1h, ha_low_1h, ha_close_1h)
condLong2h = positive_timed_trigger(ha_open_2h, ha_high_2h, ha_low_2h, ha_close_2h)
condLong2h_cci = positive_timed_trigger_1min(ha_open_2h, ha_high_2h, ha_low_2h, ha_close_2h)
condLong4h = positive_timed_trigger(ha_open_4h, ha_high_4h, ha_low_4h, ha_close_4h)
condLong4h_cci = positive_timed_trigger_1min(ha_open_4h, ha_high_4h, ha_low_4h, ha_close_4h)
condLong12h = positive_timed_trigger(ha_open_12h, ha_high_12h, ha_low_12h, ha_close_12h)
condLong1d = positive_timed_trigger(ha_open_1d, ha_high_1d, ha_low_1d, ha_close_1d)

condShort1min = negative_timed_trigger_1min(ha_open_1min, ha_high_1min, ha_low_1min, ha_close_1min)
condShort5min = negative_timed_trigger_1min(ha_open_5min, ha_high_5min, ha_low_5min, ha_close_5min)
condShort15min = negative_timed_trigger_1min(ha_open_15min, ha_high_15min, ha_low_15min, ha_close_15min)
condShort24min = negative_timed_trigger(ha_open_24min, ha_high_24min, ha_low_24min, ha_close_24min)
condShort30min = negative_timed_trigger(ha_open_30min, ha_high_30min, ha_low_30min, ha_close_30min)
condShort30min_cci = negative_timed_trigger_1min(ha_open_30min, ha_high_30min, ha_low_30min, ha_close_30min)
condShort1h = negative_timed_trigger(ha_open_1h, ha_high_1h, ha_low_1h, ha_close_1h)
condShort1h_cci = negative_timed_trigger_1min(ha_open_1h, ha_high_1h, ha_low_1h, ha_close_1h)
condShort2h = negative_timed_trigger(ha_open_2h, ha_high_2h, ha_low_2h, ha_close_2h)
condShort2h_cci = negative_timed_trigger_1min(ha_open_2h, ha_high_2h, ha_low_2h, ha_close_2h)
condShort4h = negative_timed_trigger(ha_open_4h, ha_high_4h, ha_low_4h, ha_close_4h)
condShort4h_cci = negative_timed_trigger_1min(ha_open_4h, ha_high_4h, ha_low_4h, ha_close_4h)
condShort12h = negative_timed_trigger(ha_open_12h, ha_high_12h, ha_low_12h, ha_close_12h)
condShort1d = negative_timed_trigger(ha_open_1d, ha_high_1d, ha_low_1d, ha_close_1d)


//condLong = (condLong1min and condLong5min and condLong15min and condLong30min and condLong1h and condLong1d)
//condLong = (condLong1min and condLong5min and condLong15min and condLong30min)
//condLong = condLong1min and condLong5min and condLong15min and condLong30min and condLong1h and condLong1d
//condShort = condShort1min and condShort5min and condShort15min and condShort30min and condShort1h and condShort1d
//condLong = condLong30min
//condShort = condShort30min
//condLong = (condLong1min and condLong5min and condLong30min)
condLong = condLong30min
condShort = not condLong





renko_(open_, high_, low_, close_) =>
    //hlc3_ = (ha_high_30min + ha_low_30min + ha_close_30min) / 3
    //hlc3_ = (high_30min + low_30min + close_30min) / 3
    hlc3_ = (high_ + low_ + close_) / 3
    renko_tickerid = ticker.renko(syminfo.tickerid, 'ATR', RenkoATRLength)
    renko_close = request.security(renko_tickerid, timeframe.period, hlc3_)
    //renko_close = request.security(renko_tickerid, timeframe.period, close_)
    //renko_close = request.security(renko_tickerid, timeframe.period, high_)
    //renko_close = request.security(renko_tickerid, timeframe.period, low_)
    renko_close



condRenkoLong = renko_(open_30min, high_30min, low_30min, close_30min)
plot(condRenkoLong)
//hlc3_ = (high + low + close) / 3
//hlc3_30min = (high_30min + low_30min + close_30min) / 3
//plot(hlc3_)
//plot(hlc3_30min)



indicatorColor = input(false, title='Optional bar color')
barcolor(condLong and indicatorColor ? color.lime : na)
barcolor(condShort and indicatorColor ? color.red : na)


// Submit entry orders, but only when bar is inside date range
if inDateRange
    if condLong
        strategy.entry(id='Long', direction=strategy.long)
    else
        if condShort
            //strategy.close(id="Long")
            strategy.entry(id='Short', direction=strategy.short)


// Exit open market position when date range ends
if not inDateRange
    strategy.close_all()



