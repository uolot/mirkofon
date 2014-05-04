use Rack::Static,
    :root => "web"

run lambda { |env|
    [
        200,
        {
            'Content-Type' => 'application/json',
            'Cache-Control' => 'public, max-age=86400'
        },
        File.open('web/data.json', File::RDONLY)
    ]
}
