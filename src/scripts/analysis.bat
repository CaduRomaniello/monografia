@echo OFF
cd ..
FOR /L %%x IN (1, 1, 150) DO (
    echo ================================
    echo Iteration %%x
    echo ================================
    julia main.jl newModel.json %%x 600
)
cd ./scripts
PAUSE