from bigfish.apps.visualbackend.backend.commons import get_current_term, get_klass_list

from bigfish.apps.overall.backend.ProvinceData import write_to_province_data

from bigfish.apps.overall.backend.CityData import write_to_city_data

from bigfish.apps.overall.backend.DistrictData import write_to_district_data

from bigfish.apps.overall.backend.SchoolData import write_to_school_data

from bigfish.apps.overall.backend.KlassData import write_to_klass_data


def overall_main(term, klass_list):
    write_to_klass_data(term, klass_list)
    write_to_school_data(term)
    write_to_district_data(term)
    write_to_city_data(term)
    write_to_province_data(term)


if __name__ == '__main__':
    t = get_current_term()
    k_list = get_klass_list()
    overall_main(t, k_list)
