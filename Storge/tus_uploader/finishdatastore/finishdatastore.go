package finishdatastore

import (
	// "fmt"
	"os"
	"log"
	"io"
	"path/filepath"
	// "github.com/tus/tusd/filestore"
	"../indentifierfilestore"
	"encoding/json"


)

var defaultFilePerm = os.FileMode(0777)

type FinishErr struct{
	s string
}

type MetaData struct {
    Indentifier string
    Filename string  
}

func (err *FinishErr) Error() string{
		return err.s
}

type CraeteMeataStoreFinisher struct{
	Store indentifierfilestore.FileStore
	TargetStorePath string
}

func (finisher CraeteMeataStoreFinisher) FinishUpload(id string) error {
	
	info, err := finisher.Store.GetInfo(id)
	if err != nil{
		return err
	}

	metadata := info.MetaData
	filename := metadata["filename"]
	now_file_path := filepath.Join(finisher.Store.Path, id + ".bin")
	target_file_dir := filepath.Join(finisher.TargetStorePath, id)
	if _, err := os.Stat(target_file_dir); os.IsNotExist(err) {
    	os.Mkdir(target_file_dir, defaultFilePerm)
	}
	target_file_path := filepath.Join(target_file_dir, filename)
	from, err := os.Open(now_file_path)
	if err != nil {
	  log.Fatal(err)
	}
	defer from.Close()

	to, err := os.OpenFile(target_file_path, os.O_RDWR|os.O_CREATE, 0666)
	if err != nil {
	  log.Fatal(err)
	}
	defer to.Close()

	_, err = io.Copy(to, from)
	if err != nil {
	  log.Fatal(err)
	}
	// create indentifier metadata now!
	indentifierMetadata := MetaData{
		Indentifier: id,
		Filename: filename,
	}
	jsonString, _ := json.Marshal(indentifierMetadata)
	target_metadata_path := filepath.Join(target_file_dir, "metadata")
	f, err := os.Create(target_metadata_path)
    defer f.Close()
    _, err = f.Write(jsonString)
    if err != nil {
    	return err
    }


	return nil
}