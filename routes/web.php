<?php

use App\Http\Controllers\ThalassemiaController;
use Illuminate\Support\Facades\Route;

Route::get('/', [ThalassemiaController::class, 'index'])->name('thalassemia.index');
Route::post('/predict', [ThalassemiaController::class, 'predict'])->name('thalassemia.predict');
