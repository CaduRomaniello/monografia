@REM cd ..

@REM python main.py input-seed-3-size-1000.json 1 900 nsgaII
@REM python main.py input-seed-3-size-1000.json 2 900 nsgaII
@REM python main.py input-seed-3-size-1000.json 3 900 nsgaII
@REM python main.py input-seed-3-size-1000.json 4 900 nsgaII
@REM python main.py input-seed-3-size-1000.json 5 900 nsgaII

@REM python main.py input-seed-4-size-1000.json 1 900 nsgaII
@REM python main.py input-seed-4-size-1000.json 2 900 nsgaII
@REM python main.py input-seed-4-size-1000.json 3 900 nsgaII
@REM python main.py input-seed-4-size-1000.json 4 900 nsgaII
@REM python main.py input-seed-4-size-1000.json 5 900 nsgaII

@REM cd scripts

cd ..
python mips_epsilon.py input-seed-3-size-1000.json
python mips_epsilon.py input-seed-4-size-1000.json
cd scripts