<?php

use Path/To/Db;
use Exception;

function checkFilesAvailabilityByChunk($size, $chunk_start = 0) {
	$expriredData = [];

	while (true) {
		$query = "
			SET @chunk := ".$chunk_start.";
			SELECT id,file 
			FROM images 
			WHERE id > @chunk
			ORDER BY id
			LIMIT ".$size."
			";

		// Get Chunk
		$chunk = Db::query($query);

		if (empty($chunk)) { break;	}

		foreach ($chunk as $row) {
			if (!file_exists( $row->file )) {
				$expriredData[] = $row->id;
			}
		}
		
		// Remove expired data
		// ..
		$expriredData = [];

		// Set chunk start as last id
		$chunk_start = end($chunk)->id;
	}

	return;
}

checkFilesAvailabilityByChunk(1000);
