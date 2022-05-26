
if __name__ == "__main__":
    import uvicorn
    import main
    uvicorn.run("main:app",host='0.0.0.0', port=8080, reload=True, debug=False, workers=1)

