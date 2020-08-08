import pymongo
DB = pymongo.MongoClient('localhost', 27017).yts
torrent_sizes = {}
torrent_n = {}
torrent_averages = {}
for torrent in DB.torrents.find():
    for magnet in torrent['magnets']:
        quality = magnet['quality'].split(' ').pop(0)
        quality_size = magnet['quality_size'].split(' ')
        size = float(quality_size[0])
        size_type = quality_size[1]
        if size_type == 'GB':
            size = size * 1024
        if not quality in torrent_sizes:
            torrent_sizes[quality] = 0
        if not quality in torrent_n:
            torrent_n[quality] = 0        
        torrent_n[quality] = torrent_n[quality] + 1
        torrent_sizes[quality] = torrent_sizes[quality] + size
total_disk_space_required = 0
for torrent_type in torrent_sizes:
    torrent_size = torrent_sizes[torrent_type] / torrent_n[torrent_type]
    torrent_size = torrent_size / 1024
    torrent_averages[torrent_type] = torrent_size
    torrent_size_total = torrent_sizes[torrent_type] / (1024 * 1024)
    total_disk_space_required = total_disk_space_required + torrent_size_total
    print(torrent_n[torrent_type], torrent_type, 'movies costs at average', str(torrent_size)[:4], 'GB with a total of', str(torrent_size_total)[:4], 'TB')
print('Total disk space required is', str(total_disk_space_required)[:4], 'TB')
print('Calculating (Optimal) Maximum Quality Solution')
total_disk_space_required = 0
print(torrent_n['3D'], '3D movies cost at average', str(torrent_averages['3D'])[:4], 'GB with a total of', str(torrent_averages['3D'] * torrent_n['3D'] / 1024)[:4], 'TB')
total_disk_space_required = total_disk_space_required + torrent_averages['3D'] * torrent_n['3D']
print(torrent_n['2160p'], '2160p movies cost at average', str(torrent_averages['2160p'])[:4], 'GB with a total of', str(torrent_averages['2160p'] * torrent_n['2160p'] / 1024)[:4], 'TB')
total_disk_space_required = total_disk_space_required + torrent_averages['2160p'] * torrent_n['2160p']
print(torrent_n['1080p'] - torrent_n['2160p'], '1080p movies cost at average', str(torrent_averages['1080p'])[:4], 'GB with a total of', str(torrent_averages['3D'] * (torrent_n['1080p'] - torrent_n['2160p']) / 1024)[:4], 'TB')
total_disk_space_required = total_disk_space_required + torrent_averages['1080p'] * (torrent_n['1080p'] - torrent_n['2160p'])
print(torrent_n['720p'] - torrent_n['1080p'] - torrent_n['2160p'], ' 720p movies cost at average', str(torrent_averages['720p'])[:4], 'GB with a total of', str(torrent_averages['3D'] * (torrent_n['720p'] - torrent_n['1080p'] - torrent_n['2160p']) / 1024)[:4], 'TB')
total_disk_space_required = total_disk_space_required + torrent_averages['720p'] * (torrent_n['720p'] - torrent_n['1080p'] - torrent_n['2160p'])
total_disk_space_required = total_disk_space_required / (1024)
print('Total disk space required is', str(total_disk_space_required)[:4], 'TB')